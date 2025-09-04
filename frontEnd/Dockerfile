# Use nginx as the base image
FROM nginx:alpine

# Install envsubst for environment variable substitution
RUN apk add --no-cache gettext

# Copy the static files to nginx html directory
COPY app/ /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port 80 as fallback (Railway will override with PORT env var)
EXPOSE 80

# Start the application
CMD ["/start.sh"]
