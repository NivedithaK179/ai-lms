"""
API URL routes for AI Tutor app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.ChatAPIView.as_view(), name='api-ai-chat'),
    path('history/', views.ChatHistoryListView.as_view(), name='api-chat-history'),
    path('history/clear/', views.ChatHistoryClearView.as_view(), name='api-chat-clear'),
    path('settings/<int:course_id>/', views.TutorSettingsView.as_view(), name='api-tutor-settings'),
]
