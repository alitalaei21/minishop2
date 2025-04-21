#!/bin/sh
set -e

# Wait for the Django app to be ready
echo "Waiting for Django application..."
sleep 10

echo "Starting Celery worker..."
exec "$@" 