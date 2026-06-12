"""
Frontend URL routes for courses app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.course_list_page, name='course-list'),
    path('courses/<int:pk>/', views.course_detail_page, name='course-detail'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/', views.lesson_page, name='lesson'),
    path('instructor/', views.instructor_dashboard, name='instructor-dashboard'),
    path('courses/create/', views.create_course_page, name='create-course'),
    path('courses/<int:pk>/edit/', views.edit_course_page, name='edit-course'),
]
