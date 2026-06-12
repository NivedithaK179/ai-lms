"""
Frontend URL routes for accounts app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('auth/login/', views.login_page, name='login'),
    path('auth/register/', views.register_page, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('profile/', views.profile_page, name='profile'),
    path('progress/', views.progress_page, name='progress'),
]
