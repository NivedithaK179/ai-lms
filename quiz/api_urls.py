"""
API URL routes for quiz app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuizListView.as_view(), name='api-quiz-list'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='api-quiz-detail'),
    path('<int:pk>/start/', views.QuizStartView.as_view(), name='api-quiz-start'),
    path('<int:pk>/submit/', views.QuizSubmitView.as_view(), name='api-quiz-submit'),
    path('attempts/', views.QuizAttemptListView.as_view(), name='api-quiz-attempts'),
    path('attempts/<int:pk>/', views.QuizAttemptDetailView.as_view(), name='api-quiz-attempt-detail'),
    path('create/', views.QuizCreateView.as_view(), name='api-quiz-create'),
    path('<int:quiz_id>/questions/create/', views.QuestionCreateView.as_view(), name='api-question-create'),
    path('<int:quiz_id>/delete/', views.QuizDeleteView.as_view(), name='api-quiz-delete'),
]
