from django.db.models import Case, When

from rest_framework import serializers
from .models import Quiz, Question, QuestionResponse, VisitorAnswer


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('id', 'name', 'description', 'created', 'start', 'end',)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'position', 'quiz', 'question', 'type_question',)


class QuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionResponse
        fields = ('id', 'text',)


class AddQuizSerializer(serializers.ModelSerializer):
    questions = serializers.ListField(child=serializers.DictField())

    class Meta:
        model = Quiz
        fields = ('name', 'description', 'start', 'end', 'questions',)


class VisitorAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisitorAnswer
        fields = ('visitor', 'question', 'answer', 'question_variable_answer', 'created',)


class AddAnswerSerializer(serializers.ModelSerializer):
    quiz_id = serializers.IntegerField()
    answers_list = serializers.ListField()

    class Meta:
        model = VisitorAnswer
        fields = ('quiz_id', 'answers_list')
