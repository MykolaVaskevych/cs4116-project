<?php
/**
 * Loads environment variables from a .env file.
 *
 * @param string $path Path to the .env file.
 * @throws Exception if the file does not exist.
 */
function loadEnv($path)
{
    if (!file_exists($path)) {
        throw new Exception("The .env file does not exist: $path");
    }

    // Read the file line by line, ignoring empty lines and comments
    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        // Ignore comments
        if (strpos(trim($line), '#') === 0) {
            continue;
        }
        // Split on the first "=" sign
        $parts = explode('=', $line, 2);
        if (count($parts) === 2) {
            $name = trim($parts[0]);
            $value = trim($parts[1]);
            // Remove surrounding quotes from value if present
            $value = trim($value, "\"'");
            // Set the environment variable
            putenv("$name=$value");
            $_ENV[$name] = $value;
            $_SERVER[$name] = $value;
        }
    }
}

// Load the .env file (adjust the path if necessary)
loadEnv(__DIR__ . '/.env');
