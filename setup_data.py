#!/usr/bin/env python
"""
Script to populate the database with sample data for testing.
Run with: python manage.py shell < setup_data.py
Or: python manage.py runscript setup_data (if django-extensions installed)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_core.settings')
django.setup()

from accounts.models import User
from courses.models import Category, Course, Lesson
from quiz.models import Quiz, Question, Choice

print("Creating sample data...")

# Create users
admin = User.objects.create_superuser(
    email='admin@example.com',
    password='admin123',
    first_name='Admin',
    last_name='User'
)
print(f"Created admin: {admin.email}")

instructor = User.objects.create_user(
    email='instructor@example.com',
    password='instructor123',
    first_name='Jane',
    last_name='Smith',
    role='instructor'
)
print(f"Created instructor: {instructor.email}")

student = User.objects.create_user(
    email='student@example.com',
    password='student123',
    first_name='John',
    last_name='Doe',
    role='student'
)
print(f"Created student: {student.email}")

# Create categories
categories = [
    {'name': 'Programming', 'slug': 'programming', 'icon': '💻'},
    {'name': 'Data Science', 'slug': 'data-science', 'icon': '📊'},
    {'name': 'Web Development', 'slug': 'web-development', 'icon': '🌐'},
    {'name': 'AI & Machine Learning', 'slug': 'ai-ml', 'icon': '🤖'},
]

for cat_data in categories:
    cat, created = Category.objects.get_or_create(**cat_data)
    print(f"{'Created' if created else 'Found'} category: {cat.name}")

# Create courses
programming = Category.objects.get(slug='programming')
webdev = Category.objects.get(slug='web-development')
aiml = Category.objects.get(slug='ai-ml')

courses_data = [
    {
        'title': 'Python for Beginners',
        'slug': 'python-beginners',
        'description': '''Learn Python from scratch! This comprehensive course covers all the fundamentals of Python programming.

Topics covered:
- Variables and data types
- Control flow (if/else, loops)
- Functions and modules
- Object-oriented programming
- File handling
- Error handling

Perfect for absolute beginners!''',
        'short_description': 'Master Python fundamentals with hands-on projects',
        'instructor': instructor,
        'category': programming,
        'level': 'beginner',
        'status': 'published',
        'duration_hours': 20,
        'price': 0,
    },
    {
        'title': 'Web Development with Django',
        'slug': 'web-development-django',
        'description': '''Build modern web applications with Django, Python\'s most popular web framework.

You\'ll learn:
- Django project structure
- Models and databases
- Views and templates
- Forms and validation
- User authentication
- REST APIs with DRF
- Deployment

Build real projects from scratch!''',
        'short_description': 'Build full-stack web apps with Django',
        'instructor': instructor,
        'category': webdev,
        'level': 'intermediate',
        'status': 'published',
        'duration_hours': 40,
        'price': 49.99,
    },
    {
        'title': 'Introduction to Machine Learning',
        'slug': 'intro-machine-learning',
        'description': '''Dive into the exciting world of machine learning!

Course content:
- ML fundamentals and types
- Supervised learning algorithms
- Model evaluation and validation
- Feature engineering
- Neural networks basics
- Practical projects with scikit-learn

Prerequisites: Basic Python knowledge''',
        'short_description': 'Start your journey into AI and ML',
        'instructor': instructor,
        'category': aiml,
        'level': 'intermediate',
        'status': 'published',
        'duration_hours': 30,
        'price': 79.99,
    },
]

for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        slug=course_data['slug'],
        defaults=course_data
    )
    print(f"{'Created' if created else 'Found'} course: {course.title}")

# Create lessons for Python course
python_course = Course.objects.get(slug='python-beginners')
python_lessons = [
    {
        'title': 'Welcome to Python',
        'slug': 'welcome-python',
        'content': '''# Welcome to Python!

Python is one of the most popular programming languages in the world. It's known for its simple, readable syntax that makes it perfect for beginners.

## Why Python?

- **Easy to learn**: Python's syntax is designed to be readable and intuitive
- **Versatile**: Used in web development, data science, AI, automation, and more
- **Large community**: Tons of resources, libraries, and support
- **High demand**: Python developers are highly sought after

## Setting Up

To get started, you'll need to install Python on your computer:

1. Visit [python.org](https://python.org)
2. Download the latest version
3. Follow the installation instructions
4. Open a terminal and type `python --version` to verify

Let's write our first program!

```python
print("Hello, World!")
```

Congratulations! You've just written your first Python program! 🎉''',
        'order': 0,
        'duration_minutes': 15,
        'is_free': True,
    },
    {
        'title': 'Variables and Data Types',
        'slug': 'variables-data-types',
        'content': '''# Variables and Data Types

Variables are containers for storing data values. In Python, you don't need to declare the type - it's inferred automatically!

## Creating Variables

```python
name = "Alice"      # String
age = 25            # Integer
height = 5.6        # Float
is_student = True   # Boolean
```

## Data Types

Python has several built-in data types:

### Strings
```python
greeting = "Hello"
name = 'World'
multiline = """This is a
multiline string"""
```

### Numbers
```python
integer = 42
floating = 3.14
complex_num = 1 + 2j
```

### Boolean
```python
is_active = True
is_complete = False
```

### Collections
```python
my_list = [1, 2, 3]
my_tuple = (1, 2, 3)
my_dict = {"name": "Alice", "age": 25}
my_set = {1, 2, 3}
```

## Type Checking

```python
x = 5
print(type(x))  # <class 'int'>
```

Try experimenting with different data types! 🧪''',
        'order': 1,
        'duration_minutes': 25,
        'is_free': True,
    },
    {
        'title': 'Control Flow',
        'slug': 'control-flow',
        'content': '''# Control Flow

Control flow statements allow you to control the execution of your code.

## If Statements

```python
age = 18

if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")
```

## Loops

### For Loop
```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)

# Range
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4
```

### While Loop
```python
count = 0

while count < 5:
    print(count)
    count += 1
```

## Loop Control

```python
# Break - exit the loop
for i in range(10):
    if i == 5:
        break
    print(i)

# Continue - skip to next iteration
for i in range(5):
    if i == 2:
        continue
    print(i)
```

Practice makes perfect! 🎯''',
        'order': 2,
        'duration_minutes': 30,
        'is_free': False,
    },
    {
        'title': 'Functions',
        'slug': 'functions',
        'content': '''# Functions

Functions are reusable blocks of code that perform specific tasks.

## Defining Functions

```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")
print(result)  # Hello, Alice!
```

## Parameters and Arguments

```python
# Default parameters
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Bob"))           # Hello, Bob!
print(greet("Bob", "Hi"))     # Hi, Bob!

# Keyword arguments
print(greet(greeting="Hey", name="Charlie"))
```

## *args and **kwargs

```python
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4))  # 10

def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25)
```

## Lambda Functions

```python
square = lambda x: x ** 2
print(square(4))  # 16
```

Functions are the building blocks of clean code! 🧱''',
        'order': 3,
        'duration_minutes': 35,
        'is_free': False,
    },
]

for lesson_data in python_lessons:
    lesson, created = Lesson.objects.get_or_create(
        course=python_course,
        slug=lesson_data['slug'],
        defaults=lesson_data
    )
    print(f"  {'Created' if created else 'Found'} lesson: {lesson.title}")

# Create a quiz for Python course
quiz, created = Quiz.objects.get_or_create(
    course=python_course,
    title='Python Basics Quiz',
    defaults={
        'description': 'Test your understanding of Python fundamentals',
        'pass_score': 70,
        'time_limit_minutes': 15,
    }
)
print(f"{'Created' if created else 'Found'} quiz: {quiz.title}")

# Quiz questions
questions_data = [
    {
        'text': 'What is the correct way to create a variable in Python?',
        'choices': [
            ('var x = 5', False),
            ('x = 5', True),
            ('int x = 5', False),
            ('let x = 5', False),
        ]
    },
    {
        'text': 'Which of the following is a mutable data type in Python?',
        'choices': [
            ('Tuple', False),
            ('String', False),
            ('List', True),
            ('Integer', False),
        ]
    },
    {
        'text': 'What will be the output of: print(type(3.14))?',
        'choices': [
            ('<class "int">', False),
            ('<class "float">', True),
            ('<class "str">', False),
            ('<class "number">', False),
        ]
    },
    {
        'text': 'Which keyword is used to define a function in Python?',
        'choices': [
            ('function', False),
            ('func', False),
            ('def', True),
            ('define', False),
        ]
    },
    {
        'text': 'What is the correct syntax for a for loop?',
        'choices': [
            ('for i in range(5):', True),
            ('for (i = 0; i < 5; i++)', False),
            ('for i = 0 to 5:', False),
            ('foreach i in range(5):', False),
        ]
    },
]

for i, q_data in enumerate(questions_data):
    question, created = Question.objects.get_or_create(
        quiz=quiz,
        text=q_data['text'],
        defaults={
            'order': i,
            'points': 1,
            'question_type': 'single'
        }
    )
    
    if created:
        for j, (choice_text, is_correct) in enumerate(q_data['choices']):
            Choice.objects.create(
                question=question,
                text=choice_text,
                is_correct=is_correct,
                order=j
            )
        print(f"  Created question: {question.text[:50]}...")

print("\n✅ Sample data created successfully!")
print("\nTest accounts:")
print("  Admin: admin@example.com / admin123")
print("  Instructor: instructor@example.com / instructor123")
print("  Student: student@example.com / student123")
