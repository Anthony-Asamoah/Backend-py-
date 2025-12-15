#!/bin/sh

# Exit on error
set -e

echo "Waiting for database to be ready..."
# Wait for database to be ready
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

echo "Running database migrations..."
python src/manage.py migrate

#echo "Running database seeds..."

echo "Starting application..."
exec "$@"
