"""
Models for courses app.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """Category model for organizing courses."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class name')
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Course model."""
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    preview_video = models.URLField(blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    duration_hours = models.PositiveIntegerField(default=0, help_text='Estimated hours to complete')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_free(self):
        return self.price == 0
    
    @property
    def total_lessons(self):
        return self.lessons.count()
    
    @property
    def enrolled_count(self):
        return self.enrollments.count()
    
    def publish(self):
        """Publish the course."""
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()


class Lesson(models.Model):
    """Lesson model for course content."""
    
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('mixed', 'Mixed'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField(help_text='Lesson content in HTML/Markdown')
    
    video_url = models.URLField(blank=True, help_text='YouTube or Vimeo embed URL')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text')
    
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    
    is_free = models.BooleanField(default=False, help_text='Free preview lesson')
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'slug']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    """Enrollment model - tracks student enrollment in courses."""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.email} enrolled in {self.course.title}"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed_lessons = Progress.objects.filter(
            student=self.student,
            course=self.course,
            completed=True
        ).count()
        return int((completed_lessons / total_lessons) * 100)


class Progress(models.Model):
    """Progress model - tracks lesson completion."""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Progress'
        unique_together = ['student', 'lesson']
    
    def __str__(self):
        status = 'Completed' if self.completed else 'In Progress'
        return f"{self.student.email} - {self.lesson.title} ({status})"
    
    def mark_complete(self):
        """Mark lesson as complete."""
        self.completed = True
        self.completed_at = timezone.now()
        self.save()
        
        # Check if course is completed
        enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        if enrollment.progress_percentage == 100:
            enrollment.completed = True
            enrollment.completed_at = timezone.now()
            enrollment.save()
