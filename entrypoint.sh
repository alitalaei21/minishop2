#!/bin/sh
set -e

echo "Making migrations..."
python manage.py makemigrations --noinput

echo "Handling problematic migrations..."
# First try to fake the migrations for the problematic app
python manage.py migrate produt --fake

echo "Applying migrations..."
# Then apply all other migrations
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"