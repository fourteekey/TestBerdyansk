from django.db import models
from django.conf import settings
# Create your models here.


class Quiz(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=4000)
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'quizzes'


class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    TYPE_QUESTION_CHOISES = [(0, 'Ответ текстом'),
                             (1, 'Выбрать ответ'),
                             (2, 'Выбрать несколько вариантов'),
                             ]
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    question = models.CharField(max_length=4000)
    type_question = models.IntegerField(choices=TYPE_QUESTION_CHOISES)

    def __str__(self):
        return self.question

    class Meta:
        db_table = 'questions'


# Варианты ответов на вопрос
class QuestionResponse(models.Model):
    id = models.IntegerField(primary_key=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'questions_response'


# Пользовательские ответы
class VisitorAnswer(models.Model):
    id = models.IntegerField(primary_key=True)
    visitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answer = models.CharField(max_length=1000, blank=True, null=True, default=None)
    question_variable_answer = models.ForeignKey('QuestionResponse', on_delete=models.CASCADE, blank=True, null=True,
                                                 default=None)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'visitor_answers'


# Варианты ответа выбранные пользователем.
# class VisitorAnswerResponse(models.Model):
#     id = models.IntegerField(primary_key=True)
#     visitor_answer = models.ForeignKey('VisitorAnswer', on_delete=models.CASCADE)
#     question_response = models.ForeignKey('QuestionResponse', on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = 'visitor_answers_response'

