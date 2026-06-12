"""
Models for quiz app.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Quiz(models.Model):
    """Quiz model."""
    
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quizzes'
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    pass_score = models.PositiveIntegerField(
        default=70,
        help_text='Minimum percentage required to pass'
    )
    time_limit_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Time limit in minutes (0 for no limit)'
    )
    max_attempts = models.PositiveIntegerField(
        default=0,
        help_text='Maximum attempts allowed (0 for unlimited)'
    )
    
    shuffle_questions = models.BooleanField(default=False)
    show_correct_answers = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['course', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def question_count(self):
        return self.questions.count()
    
    @property
    def total_points(self):
        return self.questions.aggregate(
            total=models.Sum('points')
        )['total'] or 0


class Question(models.Model):
    """Question model."""
    
    QUESTION_TYPES = [
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='single'
    )
    explanation = models.TextField(
        blank=True,
        help_text='Explanation shown after answering'
    )
    
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}..."
    
    @property
    def correct_choices(self):
        return self.choices.filter(is_correct=True)


class Choice(models.Model):
    """Choice model for questions."""
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        correct = '✓' if self.is_correct else '✗'
        return f"{correct} {self.text[:50]}"


class QuizAttempt(models.Model):
    """Quiz attempt model - tracks student quiz attempts."""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_points = models.PositiveIntegerField(default=0)
    earned_points = models.PositiveIntegerField(default=0)
    
    passed = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.quiz.title} ({self.score}%)"
    
    def calculate_score(self):
        """Calculate and save the score."""
        total_points = 0
        earned_points = 0
        
        for answer in self.answers.all():
            question = answer.question
            total_points += question.points
            
            if answer.is_correct:
                earned_points += question.points
        
        self.total_points = total_points
        self.earned_points = earned_points
        self.score = (earned_points / total_points * 100) if total_points > 0 else 0
        self.passed = self.score >= self.quiz.pass_score
        self.completed_at = timezone.now()
        
        if self.started_at:
            self.time_taken_seconds = int(
                (self.completed_at - self.started_at).total_seconds()
            )
        
        self.save()
        return self.score


class Answer(models.Model):
    """Answer model - tracks student answers for each question."""
    
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    selected_choices = models.ManyToManyField(
        Choice,
        blank=True,
        related_name='selected_in_answers'
    )
    
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"Answer for {self.question.text[:30]}"
    
    def check_answer(self):
        """Check if the answer is correct."""
        correct_choices = set(self.question.correct_choices.values_list('id', flat=True))
        selected = set(self.selected_choices.values_list('id', flat=True))
        self.is_correct = correct_choices == selected
        self.save()
        return self.is_correct
