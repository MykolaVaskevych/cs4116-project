# Build stage
FROM node:lts-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Run the build
RUN npm run build

# Debug: Check the build output
RUN echo "Build output structure:" && ls -la dist/ && \
    if [ -d "dist/marketplace" ]; then \
    echo "Content of dist/marketplace:" && ls -la dist/marketplace/; \
    else \
    echo "ERROR: Expected output directory dist/marketplace does not exist!"; \
    fi

# Debug: Check the contents of the index.html file
RUN if [ -f "dist/marketplace/index.html" ]; then \
    echo "First 20 lines of index.html:" && head -20 dist/marketplace/index.html; \
    else \
    echo "ERROR: index.html not found!"; \
    fi

# Production stage
FROM nginx:alpine

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Create a simple default index.html to check if Nginx is configured correctly
RUN echo '<!DOCTYPE html><html><head><title>Angular App Test</title></head><body><h1>This is a test page from the Nginx container</h1><p>If you see this, the Angular build files were not copied correctly.</p></body></html>' > /usr/share/nginx/html/index.html

# Copy the test HTML
COPY test.html /usr/share/nginx/html/test.html

# Copy the build output (this will overwrite index.html if it exists in the build output)
COPY --from=build /app/dist/marketplace/* /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Debug: Check what's in the final HTML directory
RUN echo "Final content of /usr/share/nginx/html:" && ls -la /usr/share/nginx/html/

EXPOSE 80