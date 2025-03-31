# CS4116 Project: Railway Deployment Steps

## Project Overview
- **Project Name**: CS4116 Urban Life Hub
- **Backend**: Django REST API (already deployed to Railway)
- **Frontend**: Angular application
- **Database**: MySQL (already set up on Railway)

## Step 1: Prepare Your Angular App for Deployment
I've prepared the necessary files for deployment:
- A Dockerfile in the frontend directory
- Updated environment.prod.ts to connect to the backend
- A railway.toml configuration file
- Full documentation in frontend/RAILWAY_DEPLOYMENT.md

## Step 2: Deploy the Frontend to Railway

### Method 1: Using the Railway Dashboard (Recommended for First Deploy)
1. Login to [Railway Dashboard](https://railway.app/dashboard)
2. Navigate to your existing project
3. Click "New Service" → "Deploy from GitHub repo"
4. Select your repository
5. In the settings before deployment:
   - Set Root Directory to `/frontend`
   - Set the following environment variable:
     ```
     BACKEND_URL=<your-backend-service-domain>
     ```
     (Replace with your actual backend domain from Railway)

### Method 2: Using the Railway CLI
```bash
# Navigate to the frontend directory
cd frontend

# Login to Railway
railway login

# Link to your existing project
railway link --project <your-project-id>

# Create a new service for the frontend
railway service

# Deploy the frontend
railway up

# Set the environment variable
railway variables set BACKEND_URL=<your-backend-service-domain>
```

## Step 3: Set Up Public Domain
1. After deployment, go to your frontend service in the Railway dashboard
2. Navigate to "Settings" → "Networking"
3. Click "Generate Domain" to create a public URL for your frontend

## Step 4: Connect Frontend to Backend
There are two ways to connect your frontend to the backend:

### Option 1: Using Environment Variables (Standard)
Set the `BACKEND_URL` variable to your backend's public domain:
```
BACKEND_URL=your-backend-service.railway.app
```

### Option 2: Using Private Networking (More Secure)
Use reference variables to connect via Railway's private network:
```
BACKEND_URL=${{backend-service-name.RAILWAY_PRIVATE_DOMAIN}}
```
Replace `backend-service-name` with your backend service name in Railway.

## Step 5: Verify the Deployment
1. Visit your frontend's generated domain
2. Verify that you can login and access the backend API
3. Check the logs in Railway if you encounter any issues

## Additional Resources
- Full frontend deployment documentation: `frontend/RAILWAY_DEPLOYMENT.md`
- Backend deployment documentation: `backend/RAILWAY_DEPLOYMENT.md`
- Railway Angular docs: https://docs.railway.app/guides/angular
- Railway Private Networking: https://docs.railway.app/guides/private-networking