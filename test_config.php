<?php
require_once 'src/config/config.php';

echo "Testing Configuration System...\n\n";

// Test database configuration
echo "1. Testing Database Configuration:\n";
$db_keys = ['host', 'port', 'user', 'password', 'name'];

foreach ($db_keys as $key) {
    $value = config::getDb($key);
    echo "✓ DB[$key]: " . ($key === 'PASSWORD' ? '******' : $value) . "\n";
}

// Test application configuration
echo "\n2. Testing Application Configuration:\n";
$app_keys = ['DEBUG', 'URL'];

foreach ($app_keys as $key) {
    $value = config::getApp($key);
    if (is_bool($value)) {
        $value = $value ? 'true' : 'false';
    }
    echo "✓ APP[$key]: $value\n";
}

// Test database connection
echo "\n3. Testing Database Connection:\n";
try {
    $conn = config::getDbConnection();
    echo "✓ Connected to database successfully\n";
    $conn->close();
} catch (Exception $e) {
    echo "✗ Connection error: " . $e->getMessage() . "\n";
}

echo "\nConfiguration test completed!\n";