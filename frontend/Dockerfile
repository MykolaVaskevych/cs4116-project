FROM node:lts-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Debug the build output
RUN ls -la dist/
RUN ls -la dist/marketplace/

FROM nginx:alpine

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy the build output with trailing slash to ensure contents are copied
COPY --from=build /app/dist/marketplace/ /usr/share/nginx/html/

# Create a test file to verify Nginx is serving content
RUN echo '<html><head><title>Test Page</title></head><body><h1>Test Page</h1><p>This is a test page to verify Nginx is serving content.</p></body></html>' > /usr/share/nginx/html/test.html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Debug the final content
RUN ls -la /usr/share/nginx/html/

EXPOSE 80

# Use the entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]