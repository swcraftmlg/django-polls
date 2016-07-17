from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from . import constants
from . import exceptions
from .models import Question, Choice


# def create_question(text, published=timezone.now(), choices_text=list()):
#     question = Question.objects.create(text=text, published=published)
#     for text in choices_text:
#         Choice.objects.create(question=question, text=text)
#     return question


def datetime_to_float(d):
    return float(d.strftime('%Y%m%d%H%M%S.%f'))


class QuestionTests(TestCase):

    def test_votes_without_choices(self):
        question = Question.objects.create(text='question 1', published=timezone.now())
        self.assertEqual(question.votes, 0)

    def test_votes_with_zero_voting_choices(self):
        question = Question.objects.create(text='question 1', published=timezone.now() + timedelta(days=1))
        Choice.objects.create(question=question, text='choice 1', votes=1)
        self.assertEqual(question.votes, 1)

    def test_votes(self):
        question = Question.objects.create(text='question 1')
        Choice.objects.create(text='choice 1', question=question, votes=1)
        Choice.objects.create(text='choice 2', question=question, votes=10)
        self.assertEqual(question.votes, 11)

    def test_active_future_question(self):
        question = Question(text='question 1', published=timezone.now() + timedelta(days=1))
        self.assertFalse(question.active)

    def test_active_past_question(self):
        question = Question(text='question 1')
        self.assertTrue(question.active)

    def test_active_past_closed_question(self):
        published = timezone.now() - timedelta(hours=constants.QUESTION_MIN_ACTIVE_HOURS + 1)
        question = Question(
            text='question 1',
            published=published,
            closed=published + timedelta(hours=constants.QUESTION_MIN_ACTIVE_HOURS),
        )
        self.assertFalse(question.active)

    def test_active_present_closed_question(self):
        published = timezone.now()
        question = Question(
            text='question 1',
            published=published,
            closed=published + timedelta(hours=constants.QUESTION_MIN_ACTIVE_HOURS),
        )
        self.assertTrue(question.active)

    def test_close_future_question(self):
        question = Question(text='question 1', published=timezone.now() + timedelta(days=1))
        with self.assertRaises(exceptions.QuestionError):
            question.close()

    def test_close_question_too_early(self):
        question = Question(text='question 1')
        with self.assertRaises(exceptions.QuestionError):
            question.close()

    def test_close_question(self):
        now = timezone.now()
        question = Question(
            text='question 1',
            published=now - timedelta(hours=constants.QUESTION_MIN_ACTIVE_HOURS),
        )
        question.close()
        self.assertAlmostEqual(datetime_to_float(question.closed), datetime_to_float(now), 0)


class ChoiceTests(TestCase):

    def test_increment_votes_future_question(self):
        published = timezone.now() + timedelta(days=1)
        question = Question(text='question 1', published=published)
        choice = Choice(question=question, text='choice 1')
        with self.assertRaises(exceptions.ChoiceVotingError):
            choice.increment_votes()

    def test_increment_votes_past_closed_question(self):
        now = timezone.now()
        published = now - timedelta(days=constants.QUESTION_MIN_ACTIVE_HOURS)
        question = Question(text='question 1', published=published, closed=now)
        choice = Choice(question=question, text='choice 1')
        with self.assertRaises(exceptions.ChoiceVotingError):
            choice.increment_votes()

    def test_increment_votes_active_question(self):
        published = timezone.now()
        question = Question(text='question 1', published=published)
        question.save()
        choice = Choice(question=question, text='choice 1', votes=0)
        choice.save()

        choice.increment_votes()
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)

        choice.increment_votes(2)
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 3)


class QuestionListViewTests(TestCase):

    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['latest_question_list'], [])

    def test_index_view_with_an_empty_question(self):
        """
        Questions with choices are displayed on the index page, questions
        without choices are not.
        """
        Question.objects.create(text='Past question')
        response = self.client.get(reverse('polls:list'))
        self.assertQuerysetEqual(response.context_data['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a published datetime in the past should be displayed on
        the index page.
        """
        question = Question.objects.create(text='Past question', published=timezone.now() - timedelta(days=1))
        Choice.objects.create(question=question, text='choice 1')
        response = self.client.get(reverse('polls:list'))
        self.assertQuerysetEqual(response.context_data['latest_question_list'], [repr(question)])

    def test_index_view_with_a_future_question(self):
        """
        Questions with a published datetime in the future should not be
        displayed on the index page.
        """
        question = Question.objects.create(text='Future question.', published=timezone.now() + timedelta(days=1))
        Choice.objects.create(question=question, text='choice 1')
        response = self.client.get(reverse('polls:list'))
        self.assertNotContains(response, question.text)
        self.assertQuerysetEqual(response.context_data['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        now = timezone.now()
        past_question = Question.objects.create(text='question past', published=now - timedelta(days=1))
        Choice.objects.create(question=past_question, text='choice 1')
        future_question = Question.objects.create(text='question future', published=now + timedelta(days=1))
        Choice.objects.create(question=future_question, text='choice 2')
        response = self.client.get(reverse('polls:list'))
        self.assertQuerysetEqual(response.context_data['latest_question_list'], [repr(past_question)])

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        now = timezone.now()
        question1 = Question.objects.create(text='Past question 1', published=now - timedelta(days=1))
        Choice.objects.create(question=question1, text='choice 1')
        question2 = Question.objects.create(text='Past question 2', published=now - timedelta(days=2))
        Choice.objects.create(question=question2, text='choice 2')
        response = self.client.get(reverse('polls:list'))
        self.assertQuerysetEqual(response.context_data['latest_question_list'], [repr(question1), repr(question2)])


class QuestionDetailViewTests(TestCase):

    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question that opens in the future should return a
        404 not found.
        """
        question = Question.objects.create(text='Future question.', published=timezone.now() + timedelta(days=1))
        url = reverse('polls:detail', args=[question.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question that published in the past should display
        the question's text.
        """
        question = Question.objects.create(text='Future question.', published=timezone.now() - timedelta(days=1))
        url = reverse('polls:detail', args=[question.pk])
        response = self.client.get(url)
        self.assertContains(response, question.text)
