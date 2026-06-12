web: gunicorn lms_core.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
