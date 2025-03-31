# Build stage
FROM node:lts-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy the build output
COPY --from=build /app/dist/marketplace /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Print directory contents for debugging
RUN ls -la /usr/share/nginx/html/

EXPOSE 80