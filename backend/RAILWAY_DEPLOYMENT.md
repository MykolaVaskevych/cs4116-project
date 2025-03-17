# Railway Deployment Guide

## Project Overview
- Project name: 4116 urban life hub
- Project ID: 4eb92bf5-de74-451a-b2df-525429f172a8
- Components:
  1. MySQL Database (already set up on Railway)
  2. Backend (Django) - being deployed now
  3. Frontend - will be deployed later

## Important Note for Deployment
The Dockerfile uses the `RAILWAY_SERVICE_ID` environment variable that Railway automatically provides during the build process. This is used to create properly formatted cache mounts according to Railway's specifications:

```dockerfile
# Format used for cache mounts
--mount=type=cache,id=s/${RAILWAY_SERVICE_ID}-/root/.cache/uv,target=/root/.cache/uv
```

No manual changes to the Dockerfile are needed as Railway automatically injects the `RAILWAY_SERVICE_ID` variable during build.

## Files Created/Modified for Railway Deployment

1. **Docker Files**
   - `backend/Dockerfile` - For local development
   - `backend/Dockerfile.railway` - Optimized for Railway
   - `docker-compose.yml` - Local development with MySQL
   - `docker-compose.prod.yml` - Production-ready setup

2. **Configuration Files**
   - `railway.toml` - Railway deployment configuration
   - `.dockerignore` - Files to exclude from Docker builds
   - `backend/.dockerignore` - Backend-specific exclusions
   - `backend/docker-entrypoint.sh` - Initialization script

3. **Django Settings Changes**
   - Updated `core/settings.py` to use environment variables
   - Added DATABASE_URL support with dj-database-url
   - Added health check endpoint in `core/urls.py`

## Deployment Steps

1. **Link project to Railway**
   ```bash
   railway link --project 4eb92bf5-de74-451a-b2df-525429f172a8
   ```

2. **Create a new backend service**
   ```bash
   railway service
   # Select "New Service" and then "Empty Service"
   ```

3. **Add required environment variables**
   ```bash
   railway variables set DJANGO_ENV=production
   railway variables set DJANGO_SECRET_KEY=<generate-a-secure-key>
   railway variables set ALLOWED_HOSTS=*.up.railway.app
   ```

4. **Connect to MySQL database**
   ```bash
   railway variables set MYSQL_URL=${{ MySQL.MYSQL_URL }}
   ```
   Note: Railway will automatically resolve the `${{ MySQL.MYSQL_URL }}` variable.

5. **Deploy the backend**
   ```bash
   railway up
   ```

6. **Run migrations**
   ```bash
   railway run python manage.py migrate
   ```

7. **Create a superuser (optional)**
   ```bash
   railway run python manage.py createsuperuser
   ```

## Verifying the Deployment

1. Check the deployment status:
   ```bash
   railway status
   ```

2. View the logs:
   ```bash
   railway logs
   ```

3. Visit the health check endpoint:
   ```
   https://<your-railway-domain>/api/health/
   ```

## Troubleshooting

- **Database Connection Issues**: Verify the `MYSQL_URL` variable is correctly set and accessible
- **Deployment Failures**: Check logs using `railway logs`
- **Migration Errors**: Try running migrations manually with `railway run python manage.py migrate`

## Local Development with Docker

After deployment, you can still use the Docker setup for local development:

```bash
docker-compose up --build
```

This will start the backend with a local MySQL database for development.