"""
Admin configuration for courses app.
"""

from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, Progress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'content_type', 'duration_minutes', 'is_free', 'is_published']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'level', 'status', 'price', 'created_at']
    list_filter = ['status', 'level', 'category', 'created_at']
    search_fields = ['title', 'description', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description', 'short_description')}),
        ('Details', {'fields': ('instructor', 'category', 'level', 'price', 'duration_hours')}),
        ('Media', {'fields': ('thumbnail', 'preview_video')}),
        ('Status', {'fields': ('status', 'published_at')}),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'content_type', 'duration_minutes', 'is_published']
    list_filter = ['course', 'content_type', 'is_published', 'is_free']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'completed', 'progress_percentage']
    list_filter = ['completed', 'enrolled_at', 'course']
    search_fields = ['student__email', 'course__title']
    readonly_fields = ['progress_percentage']


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed', 'course']
    search_fields = ['student__email', 'lesson__title']
