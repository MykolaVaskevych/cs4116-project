# CS4116 Project - UrbanLife

A web application that enables customers to browse business services, request inquiries, and engage in moderated discussions with service providers.

## Team Members
* 22361979 - Michal Kornacki
* 22079017 - Vivian Jently
* 22372199 - Mykola Vaskevych
* 22331549 - Nur Alislam Kastiro

## Features

- **User Roles**: Customer, Business, and Moderator roles with different permissions
- **Services**: Business users can create and manage services
- **Inquiries**: Customers can create inquiries about services
- **Messaging**: Built-in chat system between customers, businesses, and moderators
- **Wallet System**: Digital wallet with deposit, withdrawal, and transfer capabilities
- **Review System**: Customers can leave reviews for services after closed inquiries, with business owners able to respond

## Backend Setup

### Docker Setup (Recommended)

This project includes Docker support for easy local development and deployment to Railway.

#### Local Development with Docker

1. Make sure you have Docker and Docker Compose installed on your machine.

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

3. The backend will be available at http://localhost:8000

4. Docker automatically:
   - Sets up the MySQL database
   - Applies migrations
   - Creates a superuser (admin@example.com / admin123)
   - Starts the Django development server

#### Deploying to Railway

For Railway deployment, this project is configured to connect to an existing MySQL instance.

1. In your Railway project, make sure you have set up the MySQL database service.

2. Ensure the following variables are set in your Railway project:
   - `MYSQL_URL`: The MySQL connection URL (automatically connected to your MySQL service)
   - `DJANGO_SECRET_KEY`: A secure secret key for Django
   - `DJANGO_ENV`: Set to "production"
   - `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

3. Deploy using the docker-compose.prod.yml file:
   ```bash
   railway up --detach
   ```

#### Docker Commands Reference

- Start containers in development mode:
  ```bash
  docker-compose up
  ```

- Start containers in background:
  ```bash
  docker-compose up -d
  ```

- Stop containers:
  ```bash
  docker-compose down
  ```

- View logs:
  ```bash
  docker-compose logs -f
  ```

- Run migrations:
  ```bash
  docker-compose exec backend python manage.py migrate
  ```

- Create a superuser:
  ```bash
  docker-compose exec backend python manage.py createsuperuser
  ```

### Manual Setup

### Prerequisites

- Python 3.9+ 
- MySQL 8.0+ or MariaDB
- [uv](https://github.com/astral-sh/uv) package manager

#### MySQL Dependencies

**IMPORTANT**: Before installing Python dependencies, you must install system packages for the MySQL client:

**macOS**:
```bash
brew install mysql-client
```

**Ubuntu/Debian**:
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config
```

**Fedora/RHEL/CentOS**:
```bash
sudo dnf install mysql-devel python3-devel gcc
```

**Windows**:
- Install MySQL via XAMPP or standalone
- Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cs4116-project.git
cd cs4116-project
```

2. **Install dependencies using uv and activate virtual environment**
```bash
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Set up MySQL database**
   - Install MySQL or use XAMPP
   - Create a superuser (e.g., root) 
   - Create a database:
     ```bash
     mysql -u root -e "CREATE DATABASE urbanlife CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
     ```

4. **Configure database connection**

   Update `backend/my.cnf` with your MySQL credentials:
   ```
   [client]
   database = urbanlife
   user = root
   password = your_password
   default-character-set = utf8
   ```

5. **Apply migrations**
```bash
cd backend
python manage.py migrate
```

6. **Create superuser (admin)**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

The backend API will be available at http://127.0.0.1:8000/

## API Documentation

### Authentication

- Register: `POST /api/register/`
- Login: `POST /api/login/`
- Get Profile: `GET /api/profile/`
- Update Profile: `PUT/PATCH /api/profile/`

### User Roles

- **Customer** (default): Can browse services, create inquiries, and send messages
- **Business**: Can create/manage services and respond to inquiries about their services
- **Moderator**: Can view all inquiries, send messages, and close inquiries

### Wallet Operations

- Get Wallet Info: `GET /api/wallet/`
- Deposit: `POST /api/wallet/deposit/`
- Withdraw: `POST /api/wallet/withdraw/`
- Transfer: `POST /api/wallet/transfer/`
- Transaction History: `GET /api/transactions/`

### Services (Business)

- List Services: `GET /api/services/`
- List My Services: `GET /api/services/?my_services=true`
- Create Service: `POST /api/services/`
- View Service: `GET /api/services/{id}/`
- Update Service: `PUT/PATCH /api/services/{id}/`
- Delete Service: `DELETE /api/services/{id}/`

### Inquiries

- List Inquiries: `GET /api/inquiries/`
- Create Inquiry: `POST /api/inquiries/`
- View Inquiry: `GET /api/inquiries/{id}/`
- Close Inquiry (Moderator): `POST /api/inquiries/{id}/close/`

### Messages

- List Messages: `GET /api/messages/?inquiry={inquiry_id}`
- Send Message: `POST /api/messages/`

### Reviews

- List Service Reviews: `GET /api/services/{service_id}/reviews/`
- Get User Reviews: `GET /api/users/{user_id}/reviews/`
- Create Review: `POST /api/services/{service_id}/reviews/create/`
- Get Review Details: `GET /api/reviews/{review_id}/`
- Update Review: `PATCH /api/reviews/{review_id}/`
- Delete Review: `DELETE /api/reviews/{review_id}/`
- List Review Comments: `GET /api/reviews/{review_id}/comments/`
- Create Review Comment: `POST /api/reviews/{review_id}/comments/`
- Update Review Comment: `PATCH /api/reviews/{review_id}/comments/{comment_id}/`
- Delete Review Comment: `DELETE /api/reviews/{review_id}/comments/{comment_id}/`

## Testing with Bruno API Client

The project includes a collection for the [Bruno API Client](https://www.usebruno.com/) located at `backend/4116_DRF.json`, which provides ready-to-use API calls for testing all endpoints.

1. Install [Bruno](https://www.usebruno.com/downloads)
2. Open Bruno and import the collection from `backend/4116_DRF.json`
3. In the environment settings, ensure the `host` variable is set to your backend URL (default: `http://127.0.0.1:8000`)

## Troubleshooting

### MySQL Client Installation Issues

If you encounter `Error: Command "uv sync" returned non-zero exit status` related to mysqlclient:

1. **System dependencies**: Make sure you've installed all required system packages for your OS as listed above
2. **MySQL configuration**: Verify MySQL is properly installed and running
3. **Manual installation**: Try installing mysqlclient manually after meeting all dependencies:
   ```bash
   pip install mysqlclient
   ```

4. **macOS specific issues**: You might need to set compiler flags:
   ```bash
   export LDFLAGS="-L/usr/local/opt/openssl/lib"
   export CPPFLAGS="-I/usr/local/opt/openssl/include"
   ```

### Migration Issues

If you encounter migration errors:

1. Delete the database and recreate it:
   ```bash
   mysql -u root -e "DROP DATABASE urbanlife; CREATE DATABASE urbanlife CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```
2. Apply migrations again:
   ```bash
   python manage.py migrate
   ```

### Database Connection Issues

If you see database connection errors:
1. Check your `my.cnf` file has the correct credentials and database name
2. Verify the MySQL server is running
3. Try connecting directly with the mysql client:
   ```bash
   mysql -u root -p -D urbanlife
   ```
4. Ensure the database exists:
   ```bash
   mysql -u root -e "SHOW DATABASES;"
   ```