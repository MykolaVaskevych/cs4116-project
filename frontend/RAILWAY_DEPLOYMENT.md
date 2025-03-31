# Angular Frontend Deployment Guide for Railway

## Overview
This guide provides steps to deploy the Angular frontend to Railway and connect it to the existing backend service.

## Prerequisites
- Access to the Railway project where the backend is deployed
- Railway CLI installed locally (optional for CLI deployment)
- GitHub repository for the project (if deploying from GitHub)

## Deployment Steps

### 1. Create a New Service in Railway

#### Using Railway Dashboard
1. Navigate to your Railway project dashboard
2. Click "New Service" and select "Deploy from GitHub repo"
3. Select the repository containing your project
4. Configure to deploy the frontend subdirectory (`./frontend`)

#### Using Railway CLI
```bash
# Navigate to frontend directory
cd frontend

# Initialize as a Railway service
railway link --project <your-project-id>
railway service

# Deploy the frontend
railway up
```

### 2. Configure Environment Variables

Set the following environment variables for the frontend service in Railway:

```
BACKEND_URL=<your-backend-railway-domain>
```

This will be used in `environment.prod.ts` to point to your backend service.

### 3. Set Up Private Networking (Optional)

To use Railway's private networking between services:

1. In your frontend service settings, use reference variables:
   ```
   BACKEND_URL=${{backend-service-name.RAILWAY_PRIVATE_DOMAIN}}
   ```

2. Replace `backend-service-name` with the actual name of your backend service

### 4. Set Up Public Domain

1. Go to your frontend service settings
2. Navigate to "Networking" section
3. Click "Generate Domain" to create a public URL for your frontend

### 5. Verify Deployment

1. Check the deployment logs to ensure successful build
2. Visit the generated domain to verify the frontend is working
3. Test API connections to ensure the frontend can communicate with the backend

## Configuration Details

### Dockerfile
The provided Dockerfile:
- Builds the Angular app in a Node.js container
- Uses Nginx to serve the built static files
- Configures Nginx to support Angular routing

### railway.toml
The `railway.toml` file configures:
- Dockerfile as the build method
- Health check path
- Restart policies

### Environment Configuration
The `environment.prod.ts` file is configured to use the `BACKEND_URL` environment variable to connect to the backend.

## Troubleshooting

### CORS Issues
If experiencing CORS issues:
1. Verify the backend has proper CORS configuration
2. Check that the backend's `ALLOWED_HOSTS` includes the frontend domain

### Connection Issues
If the frontend cannot connect to the backend:
1. Verify the `BACKEND_URL` environment variable is set correctly
2. Check network logs in the browser console for request failures

### Build Failures
If experiencing build failures:
1. Review the deployment logs in Railway
2. Ensure all dependencies are properly listed in package.json

## Further Resources
- [Railway Angular Deployment Guide](https://docs.railway.app/guides/angular)
- [Railway Private Networking Guide](https://docs.railway.app/guides/private-networking)