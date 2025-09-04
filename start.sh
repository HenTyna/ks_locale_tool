#!/bin/bash

# Production startup script for Railway deployment

# Check if we should use Gunicorn (production) or Flask dev server
if [ "$FLASK_ENV" = "production" ]; then
    echo "Starting with Gunicorn (Production mode)..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 src.api.app:app
else
    echo "Starting with Flask dev server (Development mode)..."
    exec python src/api/app.py
fi
