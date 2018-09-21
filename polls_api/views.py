from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from polls import exceptions
from polls import models
from . import serializers


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    search_fields = ['text', 'choice__text']
    ordering_fields = ['id', 'published', 'closed', 'votes']

    @action(methods=['post'], detail=True)
    def vote(self, request, pk=None):
        question = self.get_object()
        serializer_vote = serializers.VoteSerializer(
            data=request.data,
            context={
                'question': question,
            },
        )

        serializer_vote.is_valid(raise_exception=True)
        choice_id = serializer_vote.validated_data['choice_id']
        choice = models.Choice.objects.get(pk=choice_id)

        try:
            choice.increment_votes()
            choice.refresh_from_db()
            serializer_choice = serializers.ChoiceSerializer(choice)
            return Response(data=serializer_choice.data)
        except exceptions.ChoiceVotingError as e:
            raise ValidationError(str(e))

    @action(methods=['post'], detail=True)
    def close(self, request, pk=None):
        question = self.get_object()
        try:
            question.close()
        except exceptions.QuestionError as e:
            raise ValidationError(str(e))
        return Response()
