#!/bin/sh

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=80
fi

echo "Starting nginx on port $PORT"

# Replace $PORT in nginx config with actual port
envsubst '$PORT' < /etc/nginx/conf.d/default.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/conf.d/default.conf

# Test nginx configuration
nginx -t

# Start nginx
echo "Starting nginx server..."
nginx -g 'daemon off;'
