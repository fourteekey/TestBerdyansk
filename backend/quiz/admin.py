from django.contrib import admin
from .models import Quiz, Question, QuestionResponse


# class ResponseInline(admin.StackedInline):
#     model = QuestionResponse
#     extra = 4
#
#     fields = ('text',)
#
#
# class QuestionInline(admin.StackedInline):
#     model = Question
#     extra = 1
#
#     fieldsets = (
#         (None, {
#             'fields': ('position', 'question', 'type_question',)
#         }),
#         ('Ответы', {
#             'classes': ('collapse',),
#             'fields': ('response1', 'response2', 'response3', 'response4')
#         })
#
#     )
#
#
# @admin.register(Quiz)
# class QuizAdmin(admin.ModelAdmin):
#     inlines = (QuestionInline,)
#
#     list_display = ('id', 'name', 'description', 'created', 'start', 'end',)
#     fields = ('name', 'description', 'start', 'end',)
#
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:
#             return ['start', 'end']
#         return self.readonly_fields
