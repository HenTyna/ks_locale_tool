#!/bin/bash

# Production startup script for Railway deployment

# Check if we should use Gunicorn (production) or Flask dev server
if [ "$FLASK_ENV" = "production" ]; then
    echo "Starting with Gunicorn (Production mode)..."
    exec gunicorn -c gunicorn.conf.py app:application
else
    echo "Starting with Flask dev server (Development mode)..."
    exec python app.py
fi
