FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:stable-alpine

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy the build output
COPY --from=build /app/dist/marketplace/ /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create a test file
RUN echo '<html><body><h1>Test Page</h1></body></html>' > /usr/share/nginx/html/test.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]