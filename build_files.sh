#!/bin/bash

# Install dependencies with user flag to avoid PEP 668 issues
pip install --user -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear
