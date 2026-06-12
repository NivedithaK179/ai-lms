"""
Models for AI Tutor app.
"""

from django.db import models
from django.conf import settings


class ChatHistory(models.Model):
    """Chat history model for AI Tutor conversations."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_history'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='chat_history',
        null=True,
        blank=True
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_history'
    )
    
    message = models.TextField(help_text="User's message")
    response = models.TextField(help_text="AI's response")
    
    tokens_used = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Chat Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class TutorSettings(models.Model):
    """Settings for AI Tutor behavior per course."""
    
    course = models.OneToOneField(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='tutor_settings'
    )
    
    system_prompt = models.TextField(
        blank=True,
        help_text="Custom system prompt for this course's AI tutor"
    )
    
    temperature = models.FloatField(
        default=0.7,
        help_text="AI response creativity (0.0-1.0)"
    )
    
    max_tokens = models.PositiveIntegerField(
        default=1024,
        help_text="Maximum response length"
    )
    
    is_enabled = models.BooleanField(
        default=True,
        help_text="Enable AI tutor for this course"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Tutor Settings'
    
    def __str__(self):
        return f"AI Settings for {self.course.title}"
