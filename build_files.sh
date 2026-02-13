#!/bin/bash

# Install dependencies using pipenv
pipenv install --deploy

# Collect static files
pipenv run python manage.py collectstatic --noinput --clear
