const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 80;

// Serve static files from the Angular app build directory
app.use(express.static(path.join(__dirname, 'dist/marketplace')));

// API test endpoint
app.get('/api/test', (req, res) => {
  res.json({ message: 'API is working!' });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).send('Healthy');
});

// Log all requests
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Serve a test HTML file
app.get('/test.html', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Express Server Test</title>
    </head>
    <body>
        <h1>Express Server Test Page</h1>
        <p>If you can see this page, the Express server is working.</p>
    </body>
    </html>
  `);
});

// Catch all other routes and return the index.html file
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist/marketplace/index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Current directory: ${__dirname}`);
  console.log(`Angular build path: ${path.join(__dirname, 'dist/marketplace')}`);
});