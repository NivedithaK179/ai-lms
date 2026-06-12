"""
Admin configuration for AI Tutor app.
"""

from django.contrib import admin
from .models import ChatHistory, TutorSettings


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'lesson', 'tokens_used', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['user__email', 'message', 'response']
    readonly_fields = ['user', 'course', 'lesson', 'message', 'response', 'tokens_used', 'created_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(TutorSettings)
class TutorSettingsAdmin(admin.ModelAdmin):
    list_display = ['course', 'is_enabled', 'temperature', 'max_tokens']
    list_filter = ['is_enabled']
    search_fields = ['course__title']
