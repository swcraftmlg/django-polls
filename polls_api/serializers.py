from rest_framework import serializers

from polls import models


class ChoiceSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=models.Question.objects.all(),
        required=False,
    )
    votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Choice


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = models.Question

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question_data = validated_data

        question = models.Question.objects.create(**question_data)
        for choice_data in choices_data:
            models.Choice.objects.create(question=question, **choice_data)

        return question


class VoteSerializer(serializers.Serializer):
    choice_id = serializers.IntegerField()

    def validate_choice_id(self, value):
        question = self.context['question']
        try:
            question.choices.get(pk=value)
        except models.Choice.DoesNotExist:
            raise serializers.ValidationError('This question does not have a choice with id {0}.'.format(value))
        return value
