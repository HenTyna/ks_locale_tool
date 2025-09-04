# Use nginx as the base image
FROM nginx:alpine

# Copy the static files to nginx html directory
COPY app/ /usr/share/nginx/html/

# Expose port 80 (nginx default)
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
