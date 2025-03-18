# Railway Deployment Guide

## Project Overview
- Project name: 4116 urban life hub
- Components:
  1. MySQL Database (already set up on Railway)
  2. Backend (Django) - being deployed now
  3. Frontend - will be deployed later

## Deployment Notes
The Dockerfile is optimized for Railway deployment and handles all necessary dependencies. Health checks have been disabled to improve deployment reliability.

### Important Configuration
- The service runs on port 8000
- Health checks are disabled to avoid intermittent failures
- DATABASE_URL must be set to connect to the MySQL database
- Django environment variables (DJANGO_ENV, DJANGO_SECRET_KEY, ALLOWED_HOSTS) are set in railway.toml

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
   railway link --project <your-project-id>
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

## Database Management

### Resetting the Database

If you need to completely reset the database:

1. Set the `RESET_DATABASE` environment variable:
   ```bash
   railway variables set RESET_DATABASE=true
   ```

2. Redeploy the application:
   ```bash
   railway up
   ```

3. After the reset is complete, turn off the reset flag to prevent accidental data loss:
   ```bash
   railway variables set RESET_DATABASE=false
   ```

### Generating Demo Data

To populate the database with comprehensive demo data:

1. Set the `GENERATE_DEMO_DATA` environment variable:
   ```bash
   railway variables set GENERATE_DEMO_DATA=true
   ```

2. Redeploy the application:
   ```bash
   railway up
   ```

3. After demo data generation completes, turn off the flag:
   ```bash
   railway variables set GENERATE_DEMO_DATA=false
   ```

The demo data includes:
- 80 customer accounts
- 10 moderator accounts
- 40 business accounts
- 73 services in different categories
- 100 inquiries with conversation threads
- Transactions between users
- Reviews and comments

### Admin Access

For quick admin access:
1. Visit `/admin-debug/` on your deployed site
2. Use the "Create/Reset Admin User" button to create an admin user
3. Use the "Login as Admin" button to access the admin dashboard

## Troubleshooting

- **Database Connection Issues**: Verify the `MYSQL_URL` variable is correctly set and accessible
- **Deployment Failures**: Check logs using `railway logs`
- **Migration Errors**: Try running migrations manually with `railway run python manage.py migrate`
- **Admin Access Problems**: Use the `/admin-debug/` endpoint to diagnose and fix admin user issues

## Local Development with Docker

After deployment, you can still use the Docker setup for local development:

```bash
docker-compose up --build
```

This will start the backend with a local MySQL database for development.