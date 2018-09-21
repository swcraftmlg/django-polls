from datetime import datetime, timedelta

from django.conf import settings
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from . import constants
from . import exceptions
from . import models


class ListView(generic.ListView):
    template_name = 'polls/list.jinja2'
    context_object_name = 'latest_question_list'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        """
        Return the latest questions.
        """
        # Show published
        queryset = models.Question.objects.filter(published__lte=timezone.now())
        # Remove questions without choices
        queryset = queryset.filter(choice__isnull=False).distinct()
        # Annotate query to order active questions before closed questions
        queryset = queryset.annotate(now_or_closed=Coalesce('closed', timezone.now()))
        # Order by published datetime, closed datetime, and id
        queryset = queryset.order_by('-published', '-now_or_closed', '-id')
        return queryset

    def get_context_data(self, **kwargs):
        """
        Extend context to pass page_kwarg value instead of hard coding it.
        """
        context = {'page_kwarg': self.page_kwarg}
        context.update(kwargs)
        return super(ListView, self).get_context_data(**context)


class DetailView(generic.DetailView):
    model = models.Question

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return models.Question.objects.filter(published__lte=timezone.now())

    def get_template_names(self):
        question = self.get_object()
        template_name = 'polls/detail.jinja2'
        if question.closed is not None and question.closed < timezone.now():
            template_name = 'polls/results.jinja2'
        return template_name


class ResultsView(generic.DetailView):
    model = models.Question
    template_name = 'polls/results.jinja2'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return models.Question.objects.filter(published__lte=timezone.now())


def vote(request, question_id):
    question = get_object_or_404(models.Question, pk=question_id)

    ###########################################################################
    # Check the user did not vote for this question recently
    cookie_key = 'q{0}'.format(question.pk)
    cookie_format = '{counter}{separator}{expiration}'
    cookie_value_separator = ':'
    cookie_datetime_format = '%Y-%m-%dT%H:%M:%S%z'
    remaining_votes = constants.CUOTA_VOTES_MAX_AMOUNT
    cookie_expiration = timezone.now() + timedelta(hours=constants.CUOTA_VOTES_TIMESPAN_HOURS)

    cookie_value = cookie_format.format(
        counter=remaining_votes,
        separator=cookie_value_separator,
        expiration=cookie_expiration.strftime(cookie_datetime_format),
    )
    cookie_value = request.COOKIES.get(cookie_key, cookie_value)

    try:
        raw_remaining_votes, raw_cookie_expiration = cookie_value.split(cookie_value_separator, 1)
        remaining_votes = int(raw_remaining_votes)
        cookie_expiration = datetime.strptime(raw_cookie_expiration, cookie_datetime_format)
    except (TypeError, ValueError):
        pass

    if not (remaining_votes > 0):
        return render(request, 'polls/detail.jinja2', {
            'question': question,
            'error_message': 'You have to wait for voting again.',
        })
    ###########################################################################

    try:
        selected_choice = question.choices.get(pk=request.POST['choice'])
        selected_choice.increment_votes()
    except (KeyError, models.Choice.DoesNotExist):
        return render(request, 'polls/detail.jinja2', {
            'question': question,
            'error_message': 'You have to select a choice.',
        })
    except exceptions.ChoiceVotingError:
        return render(request, 'polls/detail.jinja2', {
            'question': question,
            'error_message': 'You can not vote for this question.',
        })
    else:
        # Always return an HttpResponseRedirect after successfully dealing with
        # POST data. This prevents data from being posted twice if a user hits
        # the Back button.
        response = HttpResponseRedirect(reverse('polls:results', args=[question.id]))

        #######################################################################
        # Set a cookie to mark a recent vote from a user
        response.set_cookie(
            key=cookie_key,
            value=cookie_format.format(
                counter=remaining_votes - 1,
                separator=cookie_value_separator,
                expiration=cookie_expiration.strftime(cookie_datetime_format),
            ),
            expires=cookie_expiration,
        )
        #######################################################################

        return response
