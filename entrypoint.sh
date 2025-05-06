#!/bin/sh
set -e

echo "Making migrations..."
python manage.py makemigrations --noinput
echo "Applying migrations..."
# Then apply all other migrations
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"