"""
Frontend URL routes for quiz app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('manage/<int:course_id>/', views.manage_quizzes_page, name='quiz-manage'),
    path('create/<int:course_id>/', views.create_quiz_page, name='quiz-create'),
    path('<int:quiz_id>/questions/', views.quiz_questions_page, name='quiz-questions'),
    path('<int:pk>/', views.quiz_page, name='quiz'),
    path('result/<int:attempt_id>/', views.quiz_result_page, name='quiz-result'),
]
