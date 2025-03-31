#!/bin/bash
# This script helps debug the Docker build process locally

# Build the Angular app
echo "Building Angular app..."
npm run build

# Check the build output directory structure
echo "Build output directory structure:"
ls -la dist/

# Check if the expected output directory exists
if [ -d "dist/marketplace" ]; then
  echo "Expected output directory dist/marketplace exists!"
  echo "Content of dist/marketplace:"
  ls -la dist/marketplace/
else
  echo "ERROR: Expected output directory dist/marketplace does not exist!"
  echo "Please check your angular.json outputPath configuration."
fi

echo "Done!"