"""
Views for AI Tutor app.
"""

from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

import anthropic

from .models import ChatHistory, TutorSettings
from .serializers import (
    ChatMessageSerializer, ChatResponseSerializer,
    ChatHistorySerializer, TutorSettingsSerializer
)
from courses.models import Course, Lesson, Enrollment


class ChatAPIView(APIView):
    """AI Tutor chat endpoint."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        print("Post method hit")
        print("USER:", request.user)
        print("AUTH:", request.user.is_authenticated)
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.validated_data['message']
        #return Response({"response": "Test bot working"})
        course_id = serializer.validated_data.get('course_id')
        lesson_id = serializer.validated_data.get('lesson_id')
        
        # Get course context if provided
        course = None
        lesson = None
        system_prompt = self._get_default_system_prompt()
        
        if course_id:
            course = get_object_or_404(Course, pk=course_id)
            
            # Check enrollment
           # if not Enrollment.objects.filter(
            #    student=request.user, course=course
            #).exists() and course.instructor != request.user:
           #     return Response(
            #        {'error': 'You must be enrolled in this course to use the AI tutor.'},
             #       status=status.HTTP_403_FORBIDDEN
              #  )
            
            # Check if AI tutor is enabled
            try:
                tutor_settings = course.tutor_settings
                if not tutor_settings.is_enabled:
                    return Response(
                        {'error': 'AI tutor is not enabled for this course.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if tutor_settings.system_prompt:
                    system_prompt = tutor_settings.system_prompt
            except TutorSettings.DoesNotExist:
                pass
            
            # Add course context to system prompt
            system_prompt += f"\n\nCourse Context:\n- Course: {course.title}\n- Description: {course.description}"
            
            if lesson_id:
                lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
                system_prompt += f"\n- Current Lesson: {lesson.title}\n- Lesson Content: {lesson.content[:1000]}"
        
        # Get recent chat history for context
       # recent_chats = ChatHistory.objects.filter(
        #    user=request.user,
         #   course=course
        #).order_by('-created_at')[:5]
        recent_chats = []
        # Build messages for API
        messages = []
        
        # Add recent history (reversed to chronological order)
        for chat in reversed(list(recent_chats)):
            messages.append({"role": "user", "content": chat.message})
            messages.append({"role": "assistant", "content": chat.response})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call Anthropic API
        try:
            response_text, tokens_used = self._call_anthropic(
                system_prompt, messages
            )
        except Exception as e:
            print(f"AI error: {str(e)}")
            return Response(
                {'error': f'AI service error: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Save chat history
        if request.user.is_authenticated:
            chat_history = ChatHistory.objects.create(
                user=request.user,
                course=course,
                lesson=lesson,
                message=message,
                response=response_text,
                tokens_used=tokens_used
            )
        chat_id = chat_history.id if request.user.is_authenticated else None
        return Response({
            'response': response_text,
            'chat_id': chat_id,
            'tokens_used': tokens_used
        })
    
    def _get_default_system_prompt(self):
        return """You are an AI learning assistant for an online learning management system. 
Your role is to help students understand course material, answer questions, and provide guidance.

Guidelines:
- Be helpful, encouraging, and patient
- Explain concepts clearly with examples when appropriate
- If you don't know something, admit it honestly
- Encourage students to think critically
- Keep responses concise but comprehensive
- Use markdown formatting for better readability
- If a question is outside the course scope, politely redirect"""
    
    def _call_anthropic(self, system_prompt, messages):
        import google.generativeai as genai

        api_key = settings.GEMINI_API_KEY

        if not api_key:
            raise Exception("Gemini API key not configured")
        
       
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        user_message = messages[-1]["content"]

        response = model.generate_content(
            f"{system_prompt}\n\nStudent Question:\n{user_message}")
    

        return response.text, 0


class ChatHistoryListView(generics.ListAPIView):
    """List user's chat history."""
    
    serializer_class = ChatHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ChatHistory.objects.filter(user=self.request.user)
        
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset


class ChatHistoryClearView(APIView):
    """Clear chat history."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        course_id = request.query_params.get('course')
        
        queryset = ChatHistory.objects.filter(user=request.user)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        count = queryset.count()
        queryset.delete()
        
        return Response({
            'message': f'Deleted {count} chat messages'
        })


class TutorSettingsView(generics.RetrieveUpdateAPIView):
    """Get/Update AI Tutor settings for a course."""
    
    serializer_class = TutorSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, pk=course_id)
        
        # Only course instructor can manage settings
        if course.instructor != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the course instructor can manage AI tutor settings.")
        
        settings_obj, _ = TutorSettings.objects.get_or_create(course=course)
        return settings_obj
