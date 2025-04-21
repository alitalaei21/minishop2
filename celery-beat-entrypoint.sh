#!/bin/sh
set -e

# Wait for the Celery worker to be ready
echo "Waiting for Celery worker..."
sleep 15

echo "Starting Celery beat scheduler..."
exec "$@" 