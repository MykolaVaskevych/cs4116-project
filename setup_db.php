<?php
// Include the reusable .env loader
require_once 'env.php';

// Retrieve database credentials from environment variables
$host     = getenv('DB_HOST');
$port     = getenv('DB_PORT');
$user     = getenv('DB_USER');
$password = getenv('DB_PASSWORD');
$dbName   = getenv('DB_NAME');

// Connect to MySQL server (without selecting a default database)
$conn = new mysqli($host, $user, $password, "", $port);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// --- TMP Section: Drop the existing database if it exists ---
$dropQuery = "DROP DATABASE IF EXISTS $dbName";
if ($conn->query($dropQuery) === TRUE) {
    echo "Database '$dbName' dropped successfully (if it existed).\n";
} else {
    echo "Error dropping database: " . $conn->error . "\n";
}

// --- End TMP Section ---

// Create the database
$sql = "CREATE DATABASE IF NOT EXISTS $dbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci";
if ($conn->query($sql) === TRUE) {
    echo "Database '$dbName' created successfully.\n";
} else {
    die("Error creating database: " . $conn->error);
}

// Select the database
$conn->select_db($dbName);

// Array of table creation queries
$tableQueries = [

    // Users table
    "CREATE TABLE IF NOT EXISTS users (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         username TEXT NOT NULL,
         email TEXT NOT NULL,
         pass_hash TEXT NOT NULL,
         role TEXT NOT NULL,
         business_info TEXT,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     ) ENGINE=InnoDB",

    // Categories table
    "CREATE TABLE IF NOT EXISTS categories (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         name TEXT NOT NULL
     ) ENGINE=InnoDB",

    // Services table
    "CREATE TABLE IF NOT EXISTS services (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         provider_id BIGINT,
         name TEXT NOT NULL,
         category_id BIGINT,
         description TEXT,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (provider_id) REFERENCES users(id),
         FOREIGN KEY (category_id) REFERENCES categories(id)
     ) ENGINE=InnoDB",

    // Inquiries table
    "CREATE TABLE IF NOT EXISTS inquiries (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         customer_id BIGINT,
         service_id BIGINT,
         moderator_id BIGINT,
         status TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         negotiated_price DECIMAL(10,2),
         closed_by TEXT,
         FOREIGN KEY (customer_id) REFERENCES users(id),
         FOREIGN KEY (service_id) REFERENCES services(id),
         FOREIGN KEY (moderator_id) REFERENCES users(id)
     ) ENGINE=InnoDB",

    // Resources table
    "CREATE TABLE IF NOT EXISTS resources (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         title TEXT NOT NULL,
         content TEXT NOT NULL,
         category_id BIGINT,
         external_links TEXT,
         FOREIGN KEY (category_id) REFERENCES categories(id)
     ) ENGINE=InnoDB",

    // Messages table
    "CREATE TABLE IF NOT EXISTS messages (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         inquiry_id BIGINT,
         sender_id BIGINT,
         content TEXT NOT NULL,
         `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (inquiry_id) REFERENCES inquiries(id),
         FOREIGN KEY (sender_id) REFERENCES users(id)
     ) ENGINE=InnoDB",

    // Wallets table
    "CREATE TABLE IF NOT EXISTS wallets (
         wallet_id BIGINT AUTO_INCREMENT PRIMARY KEY,
         user_id BIGINT,
         balance DECIMAL(10,2) NOT NULL,
         FOREIGN KEY (user_id) REFERENCES users(id)
     ) ENGINE=InnoDB",

    // Transactions table
    "CREATE TABLE IF NOT EXISTS transactions (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         from_wallet_id BIGINT,
         to_wallet_id BIGINT,
         amount DECIMAL(10,2) NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         inquiry_id BIGINT,
         FOREIGN KEY (from_wallet_id) REFERENCES wallets(wallet_id),
         FOREIGN KEY (to_wallet_id) REFERENCES wallets(wallet_id),
         FOREIGN KEY (inquiry_id) REFERENCES inquiries(id)
     ) ENGINE=InnoDB",

    // Reviews table
    "CREATE TABLE IF NOT EXISTS reviews (
         id BIGINT AUTO_INCREMENT PRIMARY KEY,
         service_id BIGINT,
         customer_id BIGINT,
         rating INT NOT NULL,
         comment TEXT,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (service_id) REFERENCES services(id),
         FOREIGN KEY (customer_id) REFERENCES users(id),
         CHECK (rating >= 1 AND rating <= 5)
     ) ENGINE=InnoDB"
];

// Execute each query to create the tables
foreach ($tableQueries as $query) {
    if ($conn->query($query) === TRUE) {
        echo "Table created successfully or already exists.\n";
    } else {
        echo "Error creating table: " . $conn->error . "\n";
    }
}

// Close the connection
$conn->close();
?>
