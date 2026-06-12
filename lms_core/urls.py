"""
URL configuration for AI Learning Management System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 Endpoints
    path('api/v1/auth/', include('accounts.api_urls')),
    path('api/v1/courses/', include('courses.api_urls')),
    path('api/v1/quiz/', include('quiz.api_urls')),
    path('api/v1/ai/', include('ai_tutor.api_urls')),
    path('api/v1/progress/', include('courses.progress_urls')),
    
    # Frontend URLs
    path('', include('accounts.urls')),
    path('', include('courses.urls')),
    path('quiz/', include('quiz.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
