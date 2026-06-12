"""
Serializers for AI Tutor app.
"""

from rest_framework import serializers
from .models import ChatHistory, TutorSettings


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for chat message input."""
    
    message = serializers.CharField(max_length=2000)
    course_id = serializers.IntegerField(required=False, allow_null=True)
    lesson_id = serializers.IntegerField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response."""
    
    response = serializers.CharField()
    chat_id = serializers.IntegerField()
    tokens_used = serializers.IntegerField()


class ChatHistorySerializer(serializers.ModelSerializer):
    """Serializer for ChatHistory model."""
    
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    
    class Meta:
        model = ChatHistory
        fields = [
            'id', 'message', 'response', 'course_title',
            'lesson_title', 'tokens_used', 'created_at'
        ]


class TutorSettingsSerializer(serializers.ModelSerializer):
    """Serializer for TutorSettings model."""
    
    class Meta:
        model = TutorSettings
        fields = [
            'id', 'system_prompt', 'temperature',
            'max_tokens', 'is_enabled'
        ]
