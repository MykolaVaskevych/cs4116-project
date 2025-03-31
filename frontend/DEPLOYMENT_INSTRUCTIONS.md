# Railway Deployment Instructions

## Using the Existing Dockerfile

Our frontend directory already contains a proper Dockerfile that should work with Railway. Here's how to deploy it:

1. Create a new service in Railway:
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. Configure the root directory correctly:
   - In the service settings, set the "Root Directory" to `frontend` (without a leading slash)

3. Set the `RAILWAY_DOCKERFILE_PATH` variable:
   - In the service settings under "Variables", add:
   ```
   RAILWAY_DOCKERFILE_PATH=Dockerfile
   ```

4. Set the backend URL:
   - Add a variable for your backend:
   ```
   BACKEND_URL=https://your-backend-url.railway.app
   ```

5. Generate a domain:
   - In the "Settings" → "Networking" tab
   - Click "Generate Domain"

## Troubleshooting

If the deployment fails, try these steps:

1. Check the logs for specific error messages
2. Verify that all variables are set correctly
3. Try using the Railway CLI locally for better debugging:
   ```bash
   npm i -g @railway/cli
   railway login
   railway link
   railway up
   ```

## Using the CLI (For Local Testing)

If you want to test locally with Railway CLI:

1. Install the CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Link to your project: `railway link`
4. Deploy: `railway up`

The CLI can provide more detailed error messages and help identify deployment issues.