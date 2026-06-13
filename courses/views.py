"""
Views for courses app - both API and template views.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from .models import Category, Course, Lesson, Enrollment, Progress
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateSerializer, LessonListSerializer, LessonDetailSerializer,
    LessonCreateSerializer, EnrollmentSerializer, ProgressSerializer,
    CourseProgressSerializer
)


# =============================================================================
# Permission Classes
# =============================================================================

class IsInstructorOrAdmin(permissions.BasePermission):
    """Permission class for instructor/admin only actions."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['instructor', 'admin']
        )


class IsEnrolledOrInstructor(permissions.BasePermission):
    """Permission to access course content."""
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Lesson):
            course = obj.course
        else:
            course = obj
        
        # Allow if user is instructor
        if course.instructor == request.user:
            return True
        
        # Allow if lesson is free
        if isinstance(obj, Lesson) and obj.is_free:
            return True
        
        # Allow if enrolled
        return Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()


# =============================================================================
# API Views - Categories
# =============================================================================

class CategoryListView(generics.ListAPIView):
    """List all categories."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# =============================================================================
# API Views - Courses
# =============================================================================

class CourseListCreateView(generics.ListCreateAPIView):
    """List courses or create new course (instructors only)."""
    
    queryset = Course.objects.filter(status='published')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsInstructorOrAdmin()]
        return [permissions.AllowAny()]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateSerializer
        return CourseListSerializer
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a course."""
    
    queryset = Course.objects.all()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsInstructorOrAdmin()]
        return [permissions.AllowAny()]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseCreateSerializer
        return CourseDetailSerializer


class CourseEnrollView(APIView):
    """Enroll in a course."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, status='published')
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'error': 'You are already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course
        )
        
        return Response({
            'message': f'Successfully enrolled in {course.title}',
            'enrollment': EnrollmentSerializer(enrollment).data
        }, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(generics.ListAPIView):
    """List user's enrollments."""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)


class InstructorCoursesView(generics.ListAPIView):
    """List courses created by the instructor."""
    
    serializer_class = CourseListSerializer
    permission_classes = [IsInstructorOrAdmin]
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


# =============================================================================
# API Views - Lessons
# =============================================================================

class LessonListView(generics.ListAPIView):
    """List lessons for a course."""
    
    serializer_class = LessonListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lesson.objects.filter(course_id=course_id, is_published=True)


class LessonDetailView(generics.RetrieveAPIView):
    """Get lesson detail."""
    
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrolledOrInstructor]
    
    def get_queryset(self):
        return Lesson.objects.filter(is_published=True)


class LessonCreateView(generics.CreateAPIView):
    """Create a lesson (instructors only)."""
    
    serializer_class = LessonCreateSerializer
    permission_classes = [IsInstructorOrAdmin]
    
    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, pk=course_id, instructor=self.request.user)
        serializer.save(course=course)


class LessonCompleteView(APIView):
    """Mark a lesson as complete."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        
        # Check enrollment
        if not Enrollment.objects.filter(
            student=request.user, course=lesson.course
        ).exists():
            return Response(
                {'error': 'You are not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create or update progress
        progress, created = Progress.objects.get_or_create(
            student=request.user,
            course=lesson.course,
            lesson=lesson
        )
        
        if not progress.completed:
            progress.mark_complete()
        
        # Get updated enrollment progress
        enrollment = Enrollment.objects.get(
            student=request.user, course=lesson.course
        )
        
        return Response({
            'message': 'Lesson marked as complete',
            'progress': ProgressSerializer(progress).data,
            'course_progress': enrollment.progress_percentage
        })


# =============================================================================
# API Views - Progress
# =============================================================================

class CourseProgressView(APIView):
    """Get progress for a specific course."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        
        # Check enrollment
        try:
            enrollment = Enrollment.objects.get(
                student=request.user, course=course
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'You are not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all progress records
        progress_records = Progress.objects.filter(
            student=request.user, course=course
        )
        
        data = {
            'course_id': course.id,
            'course_title': course.title,
            'total_lessons': course.total_lessons,
            'completed_lessons': progress_records.filter(completed=True).count(),
            'progress_percentage': enrollment.progress_percentage,
            'lessons': ProgressSerializer(progress_records, many=True).data
        }
        
        return Response(data)


class AllProgressView(APIView):
    """Get progress for all enrolled courses."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user)
        
        data = []
        for enrollment in enrollments:
            progress_records = Progress.objects.filter(
                student=request.user, course=enrollment.course
            )
            
            data.append({
                'course_id': enrollment.course.id,
                'course_title': enrollment.course.title,
                'thumbnail': enrollment.course.thumbnail.url if enrollment.course.thumbnail else None,
                'total_lessons': enrollment.course.total_lessons,
                'completed_lessons': progress_records.filter(completed=True).count(),
                'progress_percentage': enrollment.progress_percentage,
                'enrolled_at': enrollment.enrolled_at,
                'completed': enrollment.completed
            })
        
        return Response(data)


# =============================================================================
# Template Views
# =============================================================================

def course_list_page(request):
    """Course listing page."""
    return render(request, 'courses/list.html')


def course_detail_page(request, pk):
    """Course detail page."""
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/detail.html', {'course_id': pk})


@login_required
def lesson_page(request, course_id, lesson_id):
    """Lesson page."""
    lesson = get_object_or_404(Lesson, pk=lesson_id, course_id=course_id)
    return render(request, 'courses/lesson.html', {
        'course_id': course_id,
        'lesson_id': lesson_id
    })


@login_required
def dashboard_page(request):
    if request.user.role in ['admin', 'instructor']:
        return redirect('instructor-dashboard')

    return render(request, 'dashboard/index.html')

@login_required
def instructor_dashboard(request):
    """Instructor dashboard for managing courses."""
    if request.user.role not in ['instructor', 'admin']:
        return render(request, 'errors/403.html', status=403)
    return render(request, 'dashboard/instructor.html')

@login_required
def create_course_page(request):
    """Create course page."""
    if request.user.role not in ['instructor', 'admin']:
        return render(request, 'errors/403.html', status=403)
    return render(request, 'courses/create.html')


@login_required
def edit_course_page(request, pk):
    """Edit course page."""
    course = get_object_or_404(Course, pk=pk)
    if course.instructor != request.user and request.user.role != 'admin':
        return render(request, 'errors/403.html', status=403)
    return render(request, 'courses/edit.html', {'course_id': pk})
