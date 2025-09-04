# Use nginx as the base image
FROM nginx:alpine

# Copy the static files to nginx html directory
COPY app/ /usr/share/nginx/html/

# Expose port 5500
EXPOSE 5500

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
