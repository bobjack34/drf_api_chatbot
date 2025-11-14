#!/bin/sh
set -e

echo "Waiting for Postgres..."
until nc -z db 5432; do
  sleep 1
done

echo "Running migrations..."
uv run python manage.py migrate --noinput

if [ -f ./events/fixtures/events_fixtures.json ]; then
  echo "Loading initial data..."
  uv run python manage.py loaddata ./events/fixtures/events_fixtures.json
fi

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
