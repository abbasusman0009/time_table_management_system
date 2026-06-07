#!/bin/sh
set -e

# If the first argument is 'gunicorn' (which is the default CMD)
if [ "$1" = 'gunicorn' ]; then
    echo "Applying database migrations..."
    python manage.py migrate
    
    echo "Seeding default data and admin..."
    python manage.py seed_data
fi

# Execute the command passed into this entrypoint
exec "$@"
