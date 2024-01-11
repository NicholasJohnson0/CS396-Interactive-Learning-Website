from django.contrib import admin

# Register your models here.

from quiz.models import *

#these will make questions appear in admin panel

class QuestionModelAdmin(admin.ModelAdmin):
    list_display = ('question', 'op1', 'op2', 'op3', 'op4', 'ans', 'max_attempts', 'subject')

class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz_question', 'selected_option', 'submission_date', 'score', 'attempts')
    list_filter = ('quiz_question', 'user')
    search_fields = ('user__username', 'quiz_question__question')
    list_per_page = 20

admin.site.register(quiz_submission, QuizSubmissionAdmin)

admin.site.register(question_model)
