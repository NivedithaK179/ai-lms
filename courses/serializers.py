"""
Serializers for courses app.
"""

from rest_framework import serializers
from .models import Category, Course, Lesson, Enrollment, Progress
from accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'course_count']
    
    def get_course_count(self, obj):
        return obj.courses.filter(status='published').count()


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer for Lesson list (minimal data)."""
    
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content_type', 'order',
            'duration_minutes', 'is_free', 'is_completed'
        ]
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Progress.objects.filter(
                student=request.user,
                lesson=obj,
                completed=True
            ).exists()
        return False


class LessonDetailSerializer(serializers.ModelSerializer):
    """Serializer for Lesson detail."""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_id = serializers.IntegerField(source='course.id', read_only=True)
    next_lesson = serializers.SerializerMethodField()
    prev_lesson = serializers.SerializerMethodField()
    
    quiz_id = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content', 'video_url', 'content_type',
            'order', 'duration_minutes', 'is_free', 'is_published',
            'course_title', 'course_id', 'quiz_id', 'next_lesson', 'prev_lesson'
        ]
    
    def get_quiz_id(self, obj):
        quiz = obj.quizzes.filter(is_published=True).first()
        return quiz.id if quiz else None

    def get_next_lesson(self, obj):
        next_lesson = Lesson.objects.filter(
            course=obj.course, order__gt=obj.order
        ).first()
        if next_lesson:
            return {'id': next_lesson.id, 'title': next_lesson.title}
        return None
    
    def get_prev_lesson(self, obj):
        prev_lesson = Lesson.objects.filter(
            course=obj.course, order__lt=obj.order
        ).last()
        if prev_lesson:
            return {'id': prev_lesson.id, 'title': prev_lesson.title}
        return None


class LessonCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating lessons."""
    
    class Meta:
        model = Lesson
        fields = [
            'title', 'slug', 'content', 'video_url', 'content_type',
            'order', 'duration_minutes', 'is_free', 'is_published'
        ]


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for Course list."""
    
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_lessons = serializers.ReadOnlyField()
    enrolled_count = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'thumbnail',
            'instructor_name', 'category_name', 'price', 'level',
            'total_lessons', 'duration_hours', 'enrolled_count', 'is_enrolled'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user, course=obj
            ).exists()
        return False


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for Course detail."""
    
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    lessons = LessonListSerializer(many=True, read_only=True)
    total_lessons = serializers.ReadOnlyField()
    enrolled_count = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'thumbnail', 'preview_video', 'instructor', 'category',
            'price', 'level', 'status', 'duration_hours',
            'total_lessons', 'enrolled_count', 'lessons',
            'is_enrolled', 'progress', 'created_at', 'published_at'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user, course=obj
            ).exists()
        return False
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(student=request.user, course=obj)
                return enrollment.progress_percentage
            except Enrollment.DoesNotExist:
                return 0
        return 0


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating courses."""
    
    class Meta:
        model = Course
        fields = ['id',
            'title', 'slug', 'description', 'short_description',
            'thumbnail', 'preview_video', 'category', 'price',
            'level', 'status', 'duration_hours'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model."""
    
    course = CourseListSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'enrolled_at', 'completed',
            'completed_at', 'progress_percentage'
        ]


class ProgressSerializer(serializers.ModelSerializer):
    """Serializer for Progress model."""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_id = serializers.IntegerField(source='lesson.id', read_only=True)
    
    class Meta:
        model = Progress
        fields = [
            'id', 'lesson_id', 'lesson_title', 'completed',
            'completed_at', 'time_spent_seconds'
        ]


class CourseProgressSerializer(serializers.Serializer):
    """Serializer for overall course progress."""
    
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    progress_percentage = serializers.IntegerField()
    lessons = ProgressSerializer(many=True)
