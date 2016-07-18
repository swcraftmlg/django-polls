from datetime import timedelta

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from . import constants
from . import exceptions


class Question(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    text = models.CharField(max_length=200)
    published = models.DateTimeField(default=timezone.now)
    closed = models.DateTimeField(blank=True, null=True)

    @property
    def votes(self):
        return self.choices.all().aggregate(votes=Coalesce(Sum('votes'), 0))['votes']

    @property
    def active(self):
        if self.closed is not None:
            return self.published <= timezone.now() <= self.closed
        else:
            return self.published <= timezone.now()

    def validate_closed(self):
        if self.closed is not None and (self.closed - self.published) < timedelta(hours=constants.QUESTION_MIN_ACTIVE_HOURS):
            raise exceptions.QuestionError(
                'The question can not be closed in less than {0} hours from publication.'.format(
                    constants.QUESTION_MIN_ACTIVE_HOURS,
                ),
            )

    def close(self):
        if self.closed is not None:
            raise exceptions.QuestionError('This question is already closed.')
        self.closed = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        self.validate_closed()
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return self.text


class Choice(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        related_query_name='choice',
    )
    text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def increment_votes(self, n=1):
        if not self.question.active:
            raise exceptions.ChoiceVotingError('Cannot vote for a closed question.')
        self.votes = models.F('votes') + n
        self.save()

    def __str__(self):
        return self.text
