"""
Views for accounts app - both API and template views.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout,login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    CustomTokenObtainPairSerializer, PasswordChangeSerializer,
    ProfileUpdateSerializer
)


# =============================================================================
# API Views
# =============================================================================

class RegisterAPIView(generics.CreateAPIView):
    """API view for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Registration successful!'
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(TokenObtainPairView):
    """API view for user login with JWT."""
    
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            login(request, user)

        return response


class LogoutAPIView(APIView):
    """API view for user logout - blacklists refresh token."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API view for getting and updating user profile."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProfileUpdateSerializer
        return UserSerializer


class PasswordChangeAPIView(APIView):
    """API view for changing password."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# Template Views
# =============================================================================

def landing_page(request):
    """Landing page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def login_page(request):
    """Login page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/login.html')


def register_page(request):
    """Registration page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/register.html')


@login_required
def dashboard_page(request):
    """Dashboard page view."""
    return render(request, 'dashboard/index.html')


@login_required
def profile_page(request):
    """Profile page view."""
    return render(request, 'dashboard/profile.html')


@login_required
def progress_page(request):
    """Progress tracking page view."""
    return render(request, 'dashboard/progress.html')


def logout_view(request):
    """Logout view."""
    auth_logout(request)
    return redirect('landing')
