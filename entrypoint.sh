#!/usr/bin/env sh
# Share env variables to all users
echo "WEBHOOK_URL=$WEBHOOK_URL" > /etc/environment

# Run sshd service
service ssh start

# Migrate database
poetry run python manage.py migrate

# Run server
poetry run python manage.py runserver 0.0.0.0:8000
