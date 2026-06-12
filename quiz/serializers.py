"""
Serializers for quiz app.
"""

from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Choice model."""
    
    class Meta:
        model = Choice
        fields = ['id', 'text', 'order']


class ChoiceWithCorrectSerializer(serializers.ModelSerializer):
    """Serializer for Choice model with correct answer (for results)."""
    
    class Meta:
        model = Choice
        fields = ['id', 'text', 'order', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model (for taking quiz)."""
    
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'points', 'explanation', 'choices']


class QuestionWithAnswerSerializer(serializers.ModelSerializer):
    """Serializer for Question with correct answers (for results)."""
    
    choices = ChoiceWithCorrectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'points', 'explanation', 'choices']


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for Quiz list."""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    question_count = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()
    user_attempts = serializers.SerializerMethodField()
    best_score = serializers.SerializerMethodField()
    is_published = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course_title',
            'pass_score', 'time_limit_minutes', 'max_attempts',
            'question_count', 'total_points', 'user_attempts', 'best_score', 'is_published'
        ]
    
    def get_user_attempts(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return QuizAttempt.objects.filter(
                student=request.user, quiz=obj
            ).count()
        return 0
    
    def get_best_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            attempt = QuizAttempt.objects.filter(
                student=request.user, quiz=obj, completed_at__isnull=False
            ).order_by('-score').first()
            if attempt:
                return float(attempt.score)
        return None


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for Quiz detail (for taking quiz)."""
    
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()
    course_id = serializers.IntegerField(source='course.id', read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'pass_score',
            'time_limit_minutes', 'shuffle_questions',
            'question_count', 'total_points', 'questions', 'course_id'
        ]


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating quizzes."""
    
    class Meta:
        model = Quiz
        fields = [
            'id','title', 'description', 'lesson', 'pass_score',
            'time_limit_minutes', 'max_attempts',
            'shuffle_questions', 'show_correct_answers', 'is_published'
        ]


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model."""
    
    selected_choice_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    
    class Meta:
        model = Answer
        fields = ['question', 'selected_choice_ids']


class AnswerResultSerializer(serializers.ModelSerializer):
    """Serializer for Answer results."""
    
    question = QuestionWithAnswerSerializer(read_only=True)
    selected_choices = ChoiceWithCorrectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Answer
        fields = ['question', 'selected_choices', 'is_correct']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for QuizAttempt model."""
    
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'score', 'total_points',
            'earned_points', 'passed', 'started_at', 'completed_at',
            'time_taken_seconds'
        ]
        read_only_fields = ['score', 'total_points', 'earned_points', 'passed', 'completed_at']


class QuizAttemptResultSerializer(serializers.ModelSerializer):
    """Serializer for QuizAttempt results."""
    
    quiz = QuizListSerializer(read_only=True)
    answers = AnswerResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'score', 'total_points', 'earned_points',
            'passed', 'started_at', 'completed_at', 'time_taken_seconds',
            'answers'
        ]


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for quiz submission."""
    
    answers = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_answers(self, value):
        """Validate answers format."""
        for answer in value:
            if 'question_id' not in answer:
                raise serializers.ValidationError('Each answer must have question_id')
            if 'choice_ids' not in answer:
                raise serializers.ValidationError('Each answer must have choice_ids')
        return value
