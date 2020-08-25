from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import *
from .serializers import *


def get_quizs(request, quiz_id=None, actual=None):
    res = []
    if quiz_id:
        quizs = [get_object_or_404(Quiz.objects.all(), id=quiz_id)]
    elif actual:
        quizs = get_list_or_404(Quiz.objects.all(), start__lte=timezone.now(), end__gte=timezone.now())
    else:
        quizs = get_list_or_404(Quiz.objects.all())

    for quiz in quizs:
        questions_list = []
        questinons = Question.objects.filter(quiz=quiz.id)
        for data in questinons:
            questions_list_dict = {
                "id": data.id,
                "question": data.question,
                "type_question": data.type_question,
            }
            if data.type_question > 0:
                question_response = QuestionResponse.objects.filter(question=data.id)
                question_response_list = QuestionResponseSerializer(question_response, many=True,
                                                                    context={"request": request}).data
                questions_list_dict.update({"questions_response": question_response_list})

            questions_list.append(questions_list_dict)

        res.append({'id': quiz.id,
                    'quiz_name': quiz.name,
                    'description': quiz.description,
                    'created': quiz.created,
                    'start': quiz.start,
                    'end': quiz.end,
                    'questions:': questions_list})
    return res


class QuizView(APIView):
    queryset = Quiz.objects.all()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('quiz_id', openapi.IN_QUERY, type='number'),
            openapi.Parameter('actual_quiz', openapi.IN_QUERY, type='boolean'),
        ]
    )
    def get(self, request, format=None):
        if request.user.is_anonymous:
            return Response({'error': 'Not authorized account'}, status=status.HTTP_401_UNAUTHORIZED)
        quiz_id = request.query_params.get('quiz_id')
        actual_quiz = request.query_params.get('actual_quiz')

        if quiz_id:
            return Response(get_quizs(request, quiz_id=quiz_id))
        elif actual_quiz:
            return Response(get_quizs(request, actual=True))
        else:
            return Response(get_quizs(request))

    @swagger_auto_schema(
        operation_description='questions content: {"question": string, ' '"type_question": int, '
                              'response_list: list[value1, value2]}\n'
                              'TYPE QUESTIONS: 0 — Ответ текстом, 1 — Выбрать ответ, 3 — Выбрать несколько вариантов\n'
                              'Для вопросов type_question = 1 или 2, полe response_list обязательны',
        request_body=AddQuizSerializer
    )
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response({'error': 'Not authorized account'}, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data
        name = request_data.get('name', None)
        description = request_data.get('description', None)
        start = request_data.get('start', None)
        end = request_data.get('end', None)
        questions = request_data.get('questions', None)

        if not name or not description or not start or not end:
            return Response({'error': 'Don\'t have required data'}, status=status.HTTP_502_BAD_GATEWAY)
        if len(questions) < 1:
            return Response({'error': 'Question list empty'}, status=status.HTTP_502_BAD_GATEWAY)

        # Проверка данных
        for data_question in questions:
            question = data_question.get('question', None)
            type_question = data_question.get('type_question', None)
            response_list = data_question.get('response_list', [])
            if not isinstance(question, str):
                return Response({'error': 'question must be str'})
            if not isinstance(type_question, int):
                return Response({'error': 'type_question must be int'})
            if 3 < type_question < -1:
                return Response({'error': 'value type_question must in (0, 1, 2)'})
            if type_question > 0 and not response_list:
                return Response({'error': 'Missing key \'response_list\': list'})
            if type_question > 0 and not isinstance(response_list, list):
                return Response({'error': 'Response must be list'})

        # #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# СОЗДАНИЕ ЗАПИСЕЙ #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
        qz = Quiz(name=name, description=description, start=start, end=end)
        qz.save()
        qz_res = Quiz.objects.latest('id')

        for data_question in questions:
            question = data_question.get('question', None)
            type_question = data_question.get('type_question', None)
            response_list = data_question.get('response_list', [])
            qt = Question(quiz=qz_res, question=question, type_question=type_question)
            qt.save()
            qt = Question.objects.latest('id')
            if response_list:
                for data in response_list:
                    qr = QuestionResponse(question=qt, text=data)
                    qr.save()
        return Response(get_quizs(request, quiz_id=qz_res.id))

    @swagger_auto_schema(
        operation_description='name: string\ndescriptions: string\nstart: str datetime\nend: str datetime'
                              '\nquestions: [{"id": int, "question": string, ' '"type_question": int, '
                              'response_list: list[{id, new_value}, {new_value}]}, '
                              '{"id": int, "question": string, "type_question": int]',
        manual_parameters=[
            openapi.Parameter('quiz_id', openapi.IN_QUERY, type='number'),
        ],
        request_body=AddQuizSerializer
    )

    # TODO: Правка, редактирование
    # можно доработать и редактировать несколько Опросников при помощи одного запроса
    # сейчас один опросник(Quiz), несколько полей
    def patch(self, request, format=None):
        if request.user.is_anonymous:
            return Response({'error': 'Not authorized account'}, status=status.HTTP_401_UNAUTHORIZED)
        quiz = get_object_or_404(self.queryset, id=request.query_params.get('quiz_id'))
        name = request.data.get('name', None)
        description = request.data.get('description', None)
        start = request.data.get('start', None)
        end = request.data.get('end', None)
        questions = request.data.get('questions', None)

        # Проверяем данные на валидность
        if name and not isinstance(name, str):
            return Response({'error': 'name must be str'}, status=status.HTTP_502_BAD_GATEWAY)
        if description and not isinstance(description, str):
            return Response({'error': 'description must be str'}, status=status.HTTP_502_BAD_GATEWAY)
        if start and not isinstance(start, str):
            return Response({'error': 'description must be str'}, status=status.HTTP_502_BAD_GATEWAY)
        if end and not isinstance(end, str):
            return Response({'error': 'description must be str'}, status=status.HTTP_502_BAD_GATEWAY)
        if questions and not isinstance(questions, list):
            return Response({'error': 'description must be str'}, status=status.HTTP_502_BAD_GATEWAY)

        if name:
            quiz.name = name
        if description:
            quiz.description = description
        if start:
            quiz.start = start
        if end:
            quiz.end = end
        quiz.save()

        if questions:
            for data_question in questions:
                id = data_question.get('id', None)
                question = data_question.get('question', None)
                type_question = data_question.get('type_question', None)
                response_list = data_question.get('response_list', None)

                if id and not isinstance(id, int):
                    return Response({'error': 'id must be int'}, status=status.HTTP_502_BAD_GATEWAY)
                if question and not isinstance(question, str):
                    return Response({'error': 'question must be str'}, status=status.HTTP_502_BAD_GATEWAY)
                if type_question and not isinstance(type_question, int):
                    return Response({'error': 'type_question must int'}, status=status.HTTP_502_BAD_GATEWAY)
                if 3 < type_question < -1:
                    return Response({'error': 'type_question must be in (0, 1, 2)'}, status=status.HTTP_502_BAD_GATEWAY)
                if response_list and not isinstance(response_list, list):
                    return Response({'error': 'response_list must be list'}, status=status.HTTP_502_BAD_GATEWAY)
                # #-#-#-#-#-#-#-#-#-#-#-#-#-#-# редактирование записи #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
                if id:
                    if type_question > 0 and not response_list:
                        return Response({'error': 'response_list can\'t be empty'},
                                        status=status.HTTP_502_BAD_GATEWAY)
                    quest = get_object_or_404(Question, id=id, quiz=quiz)
                    if questions:
                        quest.question = questions
                    if type_question == 0:
                        quest.type_question = 0
                        QuestionResponse.objects.filter(question=quest).delete()
                    if type_question in (1, 2):
                        quest.type_question = type_question
                    quest.save()
                else:
                    # #-#-#-#-#-#-#-#-#-#-#-#-#-#-# Создание новой #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
                    if not question:
                        return Response({'error': 'queestion can\'t be empty'}, status=status.HTTP_502_BAD_GATEWAY)
                    if type_question > 0 and not response_list:
                        return Response({'error': 'this type have response_list'}, status=status.HTTP_502_BAD_GATEWAY)
                    quest = Question(quiz=quiz, question=question, type_question=type_question)
                    quest.save()

                # #-#-#-#-#-#-#-#-#-#-#-#-#-#-# Создание списка ответов #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
                quest = Question.objects.get(id=id, quiz=quiz.id)
                if response_list:
                    for data in response_list:
                        id = data.get('id', None)
                        text = data.get('text', None)
                        if not text:
                            return Response({'error': 'text can\'t be empty'}, status=status.HTTP_502_BAD_GATEWAY)
                        if id and text:
                            qt_response = QuestionResponse.objects.get(id=id)
                            qt_response.text = text
                            qt_response.save()
                        else:
                            qt_response = QuestionResponse(quest=quest.id, text=text)
                            qt_response.save()

        return Response(get_quizs(request, quiz_id=request.query_params.get('quiz_id')))


class VisitorAnswerView(APIView):
    queryset = VisitorAnswer.objects.all()

    def get(self, request, format=None):
        if request.user.is_anonymous:
            return Response({'error': 'Not authorized account'}, status=status.HTTP_401_UNAUTHORIZED)
        # TODO: Можно было бы формировать словарь с такой же структурой, как при создании ответа. Могу доработать
        visitor_answers_list = get_list_or_404(self.queryset, visitor=request.user)
        return Response(VisitorAnswerSerializer(visitor_answers_list, many=True, context={"request": request}).data)

    @swagger_auto_schema(
        operation_description='quiz_id: int,  answers_list: [{question_id: int, question_response: list}]',
        request_body=AddAnswerSerializer
    )
    def post(self, request, format=None):
        if request.user.is_anonymous:
            return Response({'error': 'Not authorized account'}, status=status.HTTP_401_UNAUTHORIZED)

        request_data = request.data
        quiz_id = request_data.get('quiz_id', None)
        answers_list = request_data.get('answers_list', [])

        check = VisitorAnswer.objects.filter(question__quiz=quiz_id, visitor=request.user)
        if check:
            return Response({'error': 'Have answer on this question'}, status=status.HTTP_502_BAD_GATEWAY)

        check_actual = Quiz.objects.filter(id=quiz_id, start__lte=timezone.now(), end__gte=timezone.now())
        if not check_actual:
            return Response({'error': 'Quiz not actual. Timed left'}, status=status.HTTP_502_BAD_GATEWAY)

        # if not answers_list:
        if len(answers_list) != len(Question.objects.filter(quiz=quiz_id)):
            return Response({'error': 'answers list don\'t have all question'}, status=status.HTTP_502_BAD_GATEWAY)

        for data in answers_list:
            # Проверяем соотвествие вопроса к опроснику
            question = get_object_or_404(Question, id=data.get('question_id'), quiz=quiz_id)
            # Првоеряем на наличие ответов
            if not isinstance(data.get('question_response'), list):
                return Response(
                    Response({'error': 'question_response must be list'}, status=status.HTTP_502_BAD_GATEWAY))

            # если выбор вариантов. проверяем, чтоб указывали id варианта
            if question.type_question > 0:
                # Выбор одного варианта
                if question.type_question == 1 and len(data.get('question_response')) > 1:
                    return Response({'error': f'For id:{data.get("question_id")} data in '
                                              f'question_response must be one int element'},
                                    status=status.HTTP_502_BAD_GATEWAY)
                for qt_response in data.get('question_response'):
                    if not isinstance(qt_response, int):
                        return Response({'error': f'For id:{data.get("question_id")} data in '
                                                  f'question_response must be int'}, status=status.HTTP_502_BAD_GATEWAY)
                    get_object_or_404(QuestionResponse, id=qt_response, question=question)
            elif question.type_question == 0:
                if len(data.get('question_response')) > 1:
                    return Response({'error': f'Answer for id:{data.get("question_id")} must be text'},
                                    status=status.HTTP_502_BAD_GATEWAY)

        for data in answers_list:
            question = Question.objects.get(id=data.get('question_id'))
            if question.type_question == 0:
                record_visitor_answer = VisitorAnswer(visitor=request.user,
                                                      question=question,
                                                      answer=data.get('question_response')[0])
                record_visitor_answer.save()
            else:
                for user_question_response in data.get('question_response'):
                    visitor_answer_id = QuestionResponse.objects.get(id=user_question_response)
                    record_visitor_answer = VisitorAnswer(visitor=request.user,
                                                          question=question,
                                                          question_variable_answer=visitor_answer_id)
                    record_visitor_answer.save()

        return Response()
