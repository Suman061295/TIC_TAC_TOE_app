# Use a minimal NGINX image
FROM nginx:stable-alpine

# Remove default NGINX configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom configuration and the application files
COPY frontend/nginx.conf /etc/nginx/conf.d/simple-app.conf
COPY frontend/index.html /usr/share/nginx/html/index.html

# Expose port 80
EXPOSE 80

# NGINX starts automatically
CMD ["nginx", "-g", "daemon off;"]