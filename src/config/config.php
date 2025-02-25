<?php
/**
 * config class for application-wide configuration
 */
class config {
    /**
     * Database configuration
     */
    public static $db = [
        'host'     => '127.0.0.1',
        'port'     => 3306,
        'user'     => 'root',
        'password' => '',
        'name'     => 'urban_life'
    ];

    /**
     * Application configuration
     */
    public static $app = [
        'debug' => true,                       // Set to false in production
        'url'   => 'http://localhost/urban_life' // Base URL for the application
    ];

    /**
     * Initialize configuration settings
     * Call this at the beginning of your application
     */
    public static function init() {
        // Configure error reporting based on debug setting
        if (self::$app['debug']) {
            // Show all errors in debug mode
            ini_set('display_errors', 1);
            ini_set('display_startup_errors', 1);
            error_reporting(E_ALL);
        } else {
            // Hide errors in production
            ini_set('display_errors', 0);
            ini_set('display_startup_errors', 0);
            error_reporting(E_ALL & ~E_NOTICE & ~E_DEPRECATED & ~E_STRICT);
        }
    }

    /**
     * Get a database configuration value
     *
     * @param string $key The database config key
     * @return mixed The configuration value
     */
    public static function getDb($key) {
        return isset(self::$db[$key]) ? self::$db[$key] : null;
    }

    /**
     * Get an application configuration value
     *
     * @param string $key The application config key
     * @return mixed The configuration value
     */
    public static function getApp($key) {
        return isset(self::$app[$key]) ? self::$app[$key] : null;
    }

    /**
     * Get a database connection
     *
     * @return mysqli A database connection
     */
    public static function getDbConnection() {
        $conn = new mysqli(
            self::$db['host'],
            self::$db['user'],
            self::$db['password'],
            self::$db['name'],
            self::$db['port']
        );

        if ($conn->connect_error) {
            if (self::$app['debug']) {
                die("Database connection failed: " . $conn->connect_error);
            } else {
                die("Database connection failed. Please try again later.");
            }
        }

        return $conn;
    }
}

// Initialize settings automatically when included
config::init();