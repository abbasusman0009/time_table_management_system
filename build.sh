#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Seeding default database records (creates admin/admin123 and test data if missing)..."
python manage.py seed_data

echo "Build completed successfully!"
