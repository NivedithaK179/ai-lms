"""
API URL routes for courses app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='api-category-list'),
    
    # Courses
    path('', views.CourseListCreateView.as_view(), name='api-course-list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='api-course-detail'),
    path('<int:pk>/enroll/', views.CourseEnrollView.as_view(), name='api-course-enroll'),
    path('<int:course_id>/lessons/', views.LessonListView.as_view(), name='api-lesson-list'),
    path('<int:course_id>/lessons/create/', views.LessonCreateView.as_view(), name='api-lesson-create'),
    
    # User Enrollments
    path('my-enrollments/', views.MyEnrollmentsView.as_view(), name='api-my-enrollments'),
    path('my-courses/', views.InstructorCoursesView.as_view(), name='api-instructor-courses'),
    
    # Lessons
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='api-lesson-detail'),
    path('lessons/<int:pk>/complete/', views.LessonCompleteView.as_view(), name='api-lesson-complete'),
]
