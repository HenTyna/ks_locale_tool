#!/bin/sh

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=80
fi

# Replace $PORT in nginx config with actual port
envsubst '$PORT' < /etc/nginx/conf.d/default.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/conf.d/default.conf

# Start nginx
nginx -g 'daemon off;'
