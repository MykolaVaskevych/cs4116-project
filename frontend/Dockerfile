# Build stage
FROM node:lts-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build output
COPY --from=build /app/dist/marketplace /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Custom startup script to inject environment variables
RUN echo '#!/bin/sh\n\
cat > /usr/share/nginx/html/env-config.js << EOF\n\
window.ENV = {\n\
  BACKEND_URL: "${BACKEND_URL:-https://backend.railway.app}"\n\
};\n\
EOF\n\
\n\
sed -i "s/<head>/<head><script src=\\"env-config.js\\"><\\/script>/" /usr/share/nginx/html/index.html\n\
\n\
nginx -g "daemon off;"\n\
' > /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

CMD ["/docker-entrypoint.sh"]