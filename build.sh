#!/usr/bin/env bash
# exit on error
set -o errexit

# Install pipenv
pip install pipenv

# Install dependencies using pipenv
pipenv install --deploy --ignore-pipfile

# Collect static files
pipenv run python manage.py collectstatic --no-input

# Run migrations
pipenv run python manage.py migrate
