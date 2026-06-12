# AI Learning Management System (LMS)

A complete Learning Management System with AI-powered tutoring built with Django, Django REST Framework, and the Anthropic Claude API.

## Features

- 🔐 **User Authentication**: JWT-based authentication with role-based access (Student/Instructor/Admin)
- 📚 **Course Management**: Create, edit, and manage courses with lessons
- 🎓 **Enrollment System**: Students can enroll in courses and track progress
- 📝 **Quiz System**: Auto-graded quizzes with multiple choice questions
- 🤖 **AI Tutor**: Claude-powered AI assistant for each course
- 📊 **Progress Tracking**: Track completion and scores
- 📱 **Responsive Design**: Mobile-friendly interface
- 📖 **API Documentation**: Swagger/OpenAPI documentation

## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: HTML + CSS + JavaScript (Django Templates)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **AI**: Anthropic Claude API (claude-sonnet-4-20250514)
- **Deployment**: Render

## Project Structure

```
ai-lms/
├── lms_core/           # Django project settings
├── accounts/           # User authentication app
├── courses/            # Courses and lessons app
├── quiz/               # Quiz system app
├── ai_tutor/           # AI chatbot app
├── templates/          # HTML templates
├── static/             # CSS and JavaScript
├── requirements.txt    # Python dependencies
├── Procfile           # Render deployment
└── manage.py
```

## Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Required variables:
- `SECRET_KEY`: Django secret key
- `ANTHROPIC_API_KEY`: Your Anthropic API key for AI tutor

### 3. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login (returns JWT)
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `GET/PUT /api/v1/auth/profile/` - User profile

### Courses
- `GET /api/v1/courses/` - List all courses
- `POST /api/v1/courses/` - Create course (instructors)
- `GET /api/v1/courses/<id>/` - Course detail
- `POST /api/v1/courses/<id>/enroll/` - Enroll in course
- `GET /api/v1/courses/<id>/lessons/` - List lessons
- `GET /api/v1/courses/lessons/<id>/` - Lesson detail
- `POST /api/v1/courses/lessons/<id>/complete/` - Mark lesson complete

### Quizzes
- `GET /api/v1/quiz/?course=<id>` - List quizzes
- `GET /api/v1/quiz/<id>/` - Quiz detail
- `POST /api/v1/quiz/<id>/start/` - Start quiz attempt
- `POST /api/v1/quiz/<id>/submit/` - Submit quiz
- `GET /api/v1/quiz/attempts/` - List attempts
- `GET /api/v1/quiz/attempts/<id>/` - Attempt result

### AI Tutor
- `POST /api/v1/ai/chat/` - Chat with AI tutor
- `GET /api/v1/ai/history/` - Chat history
- `DELETE /api/v1/ai/history/clear/` - Clear history

### Progress
- `GET /api/v1/progress/` - All course progress
- `GET /api/v1/progress/<course_id>/` - Course progress

## API Documentation

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Frontend Pages

- `/` - Landing page
- `/auth/login/` - Login
- `/auth/register/` - Register
- `/dashboard/` - User dashboard
- `/courses/` - Course listing
- `/courses/<id>/` - Course detail
- `/courses/<id>/lessons/<lesson_id>/` - Lesson page with AI tutor
- `/quiz/<id>/` - Take quiz
- `/progress/` - Progress tracking

## Deployment to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables:
   - `SECRET_KEY`
   - `ANTHROPIC_API_KEY`
   - `DEBUG=False`
4. Deploy!

The `render.yaml` file includes database configuration.

## Creating Sample Data

```python
# In Django shell (python manage.py shell)

from accounts.models import User
from courses.models import Category, Course, Lesson

# Create instructor
instructor = User.objects.create_user(
    email='instructor@example.com',
    password='password123',
    first_name='John',
    last_name='Doe',
    role='instructor'
)

# Create category
category = Category.objects.create(
    name='Programming',
    slug='programming'
)

# Create course
course = Course.objects.create(
    title='Python Basics',
    slug='python-basics',
    description='Learn Python from scratch',
    instructor=instructor,
    category=category,
    status='published'
)

# Create lessons
Lesson.objects.create(
    course=course,
    title='Introduction',
    slug='introduction',
    content='Welcome to Python!',
    order=0
)
```

## License

MIT License
