"""
Admin configuration for quiz app.
"""

from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson', 'pass_score', 'question_count', 'is_published']
    list_filter = ['course', 'is_published', 'created_at']
    search_fields = ['title', 'course__title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'question_type', 'order', 'points']
    list_filter = ['quiz', 'question_type']
    search_fields = ['text', 'quiz__title']
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['text']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'passed', 'started_at', 'completed_at']
    list_filter = ['passed', 'quiz', 'started_at']
    search_fields = ['student__email', 'quiz__title']
    readonly_fields = ['score', 'total_points', 'earned_points', 'passed']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'attempt__quiz']
