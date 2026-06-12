"""
Views for quiz app - both API and template views.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quiz, Question, Choice, QuizAttempt, Answer
from .serializers import (
    QuizListSerializer, QuizDetailSerializer, QuizCreateSerializer,
    QuizAttemptSerializer, QuizAttemptResultSerializer,
    QuizSubmissionSerializer, QuestionSerializer
)
from courses.models import Course, Enrollment


# =============================================================================
# Permission Classes
# =============================================================================

class IsEnrolledInQuizCourse(permissions.BasePermission):
    """Permission to check if user is enrolled in the quiz's course."""
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Quiz):
            course = obj.course
        elif isinstance(obj, QuizAttempt):
            course = obj.quiz.course
        else:
            return False
        
        # Allow course instructor
        if course.instructor == request.user:
            return True
        
        # Check enrollment
        return Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()


# =============================================================================
# API Views
# =============================================================================

class QuizListView(generics.ListAPIView):
    """List quizzes for a course."""
    
    serializer_class = QuizListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        queryset = Quiz.objects.all()
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            if not Course.objects.filter(id=course_id, instructor=self.request.user).exists():
                queryset = queryset.filter(is_published=True)
        else:
            queryset = queryset.filter(is_published=True)
        
        return queryset


class QuizDetailView(generics.RetrieveAPIView):
    """Get quiz detail with questions."""
    
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrolledInQuizCourse]
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.kwargs.get('pk'):
            if Quiz.objects.filter(pk=self.kwargs['pk'], course__instructor=self.request.user).exists():
                return Quiz.objects.all()
        return Quiz.objects.filter(is_published=True)


class QuizStartView(APIView):
    """Start a quiz attempt."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
        
        # Check enrollment
        if not Enrollment.objects.filter(
            student=request.user, course=quiz.course
        ).exists():
            return Response(
                {'error': 'You are not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check max attempts
        if quiz.max_attempts > 0:
            attempt_count = QuizAttempt.objects.filter(
                student=request.user, quiz=quiz
            ).count()
            if attempt_count >= quiz.max_attempts:
                return Response(
                    {'error': f'Maximum attempts ({quiz.max_attempts}) reached.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check for incomplete attempt
        incomplete = QuizAttempt.objects.filter(
            student=request.user, quiz=quiz, completed_at__isnull=True
        ).first()
        
        if incomplete:
            # Return existing incomplete attempt
            return Response({
                'attempt': QuizAttemptSerializer(incomplete).data,
                'quiz': QuizDetailSerializer(quiz, context={'request': request}).data,
                'message': 'Continuing previous attempt'
            })
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz
        )
        
        return Response({
            'attempt': QuizAttemptSerializer(attempt).data,
            'quiz': QuizDetailSerializer(quiz, context={'request': request}).data,
            'message': 'Quiz started'
        }, status=status.HTTP_201_CREATED)


class QuizSubmitView(APIView):
    """Submit quiz answers."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        
        # Get the attempt
        attempt = QuizAttempt.objects.filter(
            student=request.user,
            quiz=quiz,
            completed_at__isnull=True
        ).first()
        
        if not attempt:
            return Response(
                {'error': 'No active attempt found. Start a new quiz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate submission
        serializer = QuizSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        answers_data = serializer.validated_data['answers']
        
        # Process answers
        for answer_data in answers_data:
            question_id = answer_data['question_id']
            choice_ids = answer_data['choice_ids']
            
            try:
                question = Question.objects.get(pk=question_id, quiz=quiz)
            except Question.DoesNotExist:
                continue
            
            # Create or update answer
            answer, _ = Answer.objects.get_or_create(
                attempt=attempt,
                question=question
            )
            
            # Set selected choices
            choices = Choice.objects.filter(pk__in=choice_ids, question=question)
            answer.selected_choices.set(choices)
            answer.check_answer()
        
        # Calculate final score
        attempt.calculate_score()
        
        # Prepare response
        result_serializer = QuizAttemptResultSerializer(
            attempt, context={'request': request}
        )
        
        return Response({
            'message': 'Quiz submitted successfully',
            'passed': attempt.passed,
            'result': result_serializer.data
        })


class QuizAttemptListView(generics.ListAPIView):
    """List user's quiz attempts."""
    
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(
            student=self.request.user,
            completed_at__isnull=False
        )


class QuizAttemptDetailView(generics.RetrieveAPIView):
    """Get quiz attempt result."""
    
    serializer_class = QuizAttemptResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user)


class QuizCreateView(generics.CreateAPIView):
    """Create a quiz (instructors only)."""
    
    serializer_class = QuizCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        course_id = self.request.data.get('course_id')
        from courses.models import Course
        course = get_object_or_404(Course, pk=course_id, instructor=self.request.user)
        print("REQUEST DATA:", self.request.data)
        serializer.save(course=course)

class QuizDeleteView(APIView):
    def delete(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz.delete()
            return Response(
                {"message": "Quiz deleted"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Quiz.DoesNotExist:
            return Response(
                {"error": "Quiz not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class QuestionCreateView(APIView):
    """Create a question for a quiz."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        
        # Check instructor
        if quiz.course.instructor != request.user:
            return Response(
                {'error': 'Only the course instructor can add questions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create question
        question = Question.objects.create(
            quiz=quiz,
            text=request.data.get('text'),
            question_type=request.data.get('question_type', 'single'),
            explanation=request.data.get('explanation', ''),
            order=request.data.get('order', 0),
            points=request.data.get('points', 1)
        )
        
        # Create choices
        choices_data = request.data.get('choices', [])
        for choice_data in choices_data:
            Choice.objects.create(
                question=question,
                text=choice_data.get('text'),
                is_correct=choice_data.get('is_correct', False),
                order=choice_data.get('order', 0)
            )
        
        return Response({
            'message': 'Question created',
            'question': QuestionSerializer(question).data
        }, status=status.HTTP_201_CREATED)


# =============================================================================
# Template Views
# =============================================================================

@login_required
def quiz_page(request, pk):
    """Quiz taking page."""
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quiz/take.html', {'quiz_id': pk})


@login_required
def quiz_result_page(request, attempt_id):
    """Quiz result page."""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, student=request.user)
    return render(request, 'quiz/result.html', {'attempt_id': attempt_id})


@login_required
def manage_quizzes_page(request, course_id):
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)
    return render(request, 'quiz/manage.html', {'course_id': course.id})


@login_required
def create_quiz_page(request, course_id):
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)
    return render(request, 'quiz/create.html', {'course_id': course.id})


@login_required
def quiz_questions_page(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, course__instructor=request.user)
    return render(request, 'quiz/questions.html', {'quiz_id': quiz.id})
