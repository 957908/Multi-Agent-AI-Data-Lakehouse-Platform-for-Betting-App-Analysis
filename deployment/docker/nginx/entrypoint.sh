#!/bin/sh

# Ensure SSL directory exists
mkdir -p /etc/nginx/ssl

# Generate self-signed certificate if it doesn't exist
if [ ! -f /etc/nginx/ssl/sentinelx.crt ] || [ ! -f /etc/nginx/ssl/sentinelx.key ]; then
    echo "SSL Certificate or Key not found. Generating self-signed certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/sentinelx.key \
        -out /etc/nginx/ssl/sentinelx.crt \
        -subj "/C=US/ST=State/L=City/O=SentinelX/OU=TrustAI/CN=localhost"
    echo "Self-signed certificate generated successfully."
fi

# Execute CMD (starts Nginx)
exec nginx -g "daemon off;"
