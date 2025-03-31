#!/bin/sh
set -e

# Inject environment variables into the app at runtime
cat > /usr/share/nginx/html/env-config.js << EOF
window.ENV = {
  BACKEND_URL: "${BACKEND_URL:-https://backend.railway.app}"
};
EOF

# Inject the script into the index.html file
sed -i 's/<head>/<head><script src="env-config.js"><\/script>/' /usr/share/nginx/html/index.html

# Start nginx
exec nginx -g "daemon off;"