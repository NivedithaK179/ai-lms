"""
API URL routes for accounts app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='api-register'),
    path('login/', views.LoginAPIView.as_view(), name='api-login'),
    path('logout/', views.LogoutAPIView.as_view(), name='api-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('profile/', views.UserProfileAPIView.as_view(), name='api-profile'),
    path('password/change/', views.PasswordChangeAPIView.as_view(), name='api-password-change'),
]
