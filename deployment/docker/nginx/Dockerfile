FROM nginx:1.25-alpine

# Install openssl for dynamic self-signed certificate generation
RUN apk add --no-cache openssl

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Copy configuration
COPY deployment/docker/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint script
COPY deployment/docker/nginx/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]
