from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic

from . import constants
from . import exceptions
from .models import Question, Choice


class ListView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    paginate_by = constants.PAGE_SIZE

    def get_queryset(self):
        """
        Return the latest questions.
        """
        queryset = Question.objects.filter(published__lte=timezone.now())  # Show published
        queryset = queryset.filter(choice__isnull=False).distinct()  # Remove questions without choices
        queryset = queryset.order_by('-published', '-closed', '-id')  # Order by published and closed datetime, and id
        return queryset

    def get_context_data(self, **kwargs):
        """
        Extend context to pass page_kwarg value instead of hard coding it.
        """
        context = {'page_kwarg': self.page_kwarg}
        context.update(kwargs)
        return super(ListView, self).get_context_data(**context)


class DetailView(generic.DetailView):
    model = Question

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(published__lte=timezone.now())

    def get_template_names(self):
        question = self.get_object()
        template_name = 'polls/detail.html'
        if question.closed is not None and question.closed < timezone.now():
            template_name = 'polls/results.html'
        return template_name


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(published__lte=timezone.now())


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choices.get(pk=request.POST['choice'])
        selected_choice.increment_votes()
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    except exceptions.ChoiceVotingError:
        pass

    # Always return an HttpResponseRedirect after successfully dealing with
    # POST data. This prevents data from being posted twice if a user hits the
    # Back button.
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
