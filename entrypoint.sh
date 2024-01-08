#!/bin/bash

echo "Waiting for RabbitMQ to be available..."
# Wait for RabbitMQ to be available
while ! timeout 1 bash -c 'until echo "" | nc -z docker-taskyflow-microservice-rabbitmq-container-1 5672; do sleep 1; done'; do sleep 1; done
echo "RabbitMQ is available. Running migrations..."

echo "Waiting for PostgreSQL to be available..."
# Wait for PostgreSQL to be available
while ! timeout 1 bash -c 'until echo "" | nc -z docker-taskyflow-microservice-postgres-task-1 5432; do sleep 1; done'; do sleep 1; done
echo "PostgreSQL is available. Running migrations..."

# Run migrations
python manage.py makemigrations
sleep 2
python manage.py migrate
sleep 2

echo "Migrations complete. Starting the application with Gunicorn..."
# Start the application with Gunicorn
exec gunicorn taskytaskservice.wsgi:application --bind 0.0.0.0:8200


