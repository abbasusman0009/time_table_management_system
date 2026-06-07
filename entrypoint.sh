#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate

echo "Seeding default data and admin..."
python manage.py seed_data

echo "Starting Gunicorn server..."
exec gunicorn ttms_project.wsgi:application --bind 0.0.0.0:8000
