"""
API URL routes for progress tracking.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllProgressView.as_view(), name='api-all-progress'),
    path('<int:course_id>/', views.CourseProgressView.as_view(), name='api-course-progress'),
]
