<?php
session_start();

// Include your env loader if available
// require_once 'env.php';

// For this example, we assume the .env file is loaded and these variables are set.
$host     = getenv('DB_HOST') ?: 'localhost';
$port     = getenv('DB_PORT') ?: 3306;
$dbUser   = getenv('DB_USER') ?: 'root';
$dbPass   = getenv('DB_PASSWORD') ?: '';
$dbName   = getenv('DB_NAME') ?: 'urban_life';

// Create MySQLi connection
$conn = new mysqli($host, $dbUser, $dbPass, $dbName, $port);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Message holders
$registerMsg = "";
$loginMsg    = "";

/**
 * Checks password complexity.
 *
 * Conditions:
 * - At least 5 characters long.
 * - Contains at least one uppercase letter.
 * - Contains at least one number.
 *
 * Returns "Too weak" if requirements are not met.
 * If requirements are met, returns "Strong" for passwords longer than 8 characters, otherwise "Ok".
 */
function checkPasswordComplexity($password) {
    if (strlen($password) < 5) {
        return "Too weak";
    }
    if (!preg_match('/[A-Z]/', $password)) {
        return "Too weak";
    }
    if (!preg_match('/\d/', $password)) {
        return "Too weak";
    }
    if (strlen($password) > 8) {
        return "Strong";
    }
    return "Ok";
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Registration processing
    if (isset($_POST['register'])) {
        $username = trim($_POST['username']);
        $email    = trim($_POST['email']);
        $password = $_POST['password'];

        // Validate email format using PHP's built-in filter (regex under the hood)
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $registerMsg = "Invalid email format.";
        } else {
            // Check if email already exists
            $stmt = $conn->prepare("SELECT id FROM users WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $stmt->store_result();
            if ($stmt->num_rows > 0) {
                $registerMsg = "Email already registered.";
            } else {
                // Check password complexity
                $complexity = checkPasswordComplexity($password);
                if ($complexity === "Too weak") {
                    $registerMsg = "Password too weak. Must be at least 5 characters long, include an uppercase letter and a number.";
                } else {
                    // Hash the password for storage
                    $pass_hash = password_hash($password, PASSWORD_DEFAULT);
                    // Set role to "customer" by default
                    $default_role = "customer";

                    $stmtInsert = $conn->prepare("INSERT INTO users (username, email, pass_hash, role) VALUES (?, ?, ?, ?)");
                    $stmtInsert->bind_param("ssss", $username, $email, $pass_hash, $default_role);
                    if ($stmtInsert->execute()) {
                        $registerMsg = "Registration successful. You can now login.";
                    } else {
                        $registerMsg = "Registration failed: " . $conn->error;
                    }
                    $stmtInsert->close();
                }
            }
            $stmt->close();
        }
    }

    // Login processing
    if (isset($_POST['login'])) {
        $email    = trim($_POST['email']);
        $password = $_POST['password'];

        $stmt = $conn->prepare("SELECT id, username, pass_hash FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();
        if ($result->num_rows === 1) {
            $userData = $result->fetch_assoc();
            if (password_verify($password, $userData['pass_hash'])) {
                // Login successful
                $_SESSION['user_id']   = $userData['id'];
                $_SESSION['username']  = $userData['username'];
                $loginMsg = "Login successful. Welcome, " . htmlspecialchars($userData['username']) . "!";
            } else {
                $loginMsg = "Invalid email or password.";
            }
        } else {
            $loginMsg = "Invalid email or password.";
        }
        $stmt->close();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Login &amp; Registration</title>
  <!-- Bootstrap CSS CDN -->
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
<div class="container mt-5">
  <h2 class="mb-4 text-center">User Authentication</h2>
  <div class="row">
    <!-- Login Form -->
    <div class="col-md-6">
      <h3>Login</h3>
      <?php if ($loginMsg): ?>
        <div class="alert alert-info"><?php echo $loginMsg; ?></div>
      <?php endif; ?>
      <form method="post" action="">
        <div class="form-group">
          <label for="loginEmail">Email address</label>
          <input type="email" class="form-control" id="loginEmail" name="email" placeholder="Enter email" required>
        </div>
        <div class="form-group">
          <label for="loginPassword">Password</label>
          <input type="password" class="form-control" id="loginPassword" name="password" placeholder="Password" required>
        </div>
        <button type="submit" name="login" class="btn btn-primary">Login</button>
      </form>
    </div>
    <!-- Registration Form -->
    <div class="col-md-6">
      <h3>Register</h3>
      <?php if ($registerMsg): ?>
        <div class="alert alert-info"><?php echo $registerMsg; ?></div>
      <?php endif; ?>
      <form method="post" action="">
        <div class="form-group">
          <label for="regUsername">Username</label>
          <input type="text" class="form-control" id="regUsername" name="username" placeholder="Enter username" required>
        </div>
        <div class="form-group">
          <label for="regEmail">Email address</label>
          <input type="email" class="form-control" id="regEmail" name="email" placeholder="Enter email" required>
        </div>
        <div class="form-group">
          <label for="regPassword">Password</label>
          <input type="password" class="form-control" id="regPassword" name="password" placeholder="Password" required>
          <small id="passwordHelp" class="form-text text-muted">
            Password must be at least 5 characters long, include an uppercase letter and a number.
          </small>
        </div>
        <button type="submit" name="register" class="btn btn-success">Register</button>
      </form>
    </div>
  </div>
</div>

<!-- Bootstrap JS, Popper.js, and jQuery CDN -->
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
<?php
$conn->close();
?>
