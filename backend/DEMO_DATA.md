# Demo Data Generation

This project includes a script to generate comprehensive demo data for demonstration and testing purposes. The script generates:

- 80 customer accounts
- 10 moderator accounts
- 40 business accounts
- 73 service listings in 14 different categories
- 100 inquiries with conversation threads
- Transactions between users
- Reviews and review comments

## Automatic Generation with Docker

The easiest way to generate demo data is by setting the `GENERATE_DEMO_DATA` environment variable to `true` when running the application through Docker:

```bash
docker-compose up -d
```

The `docker-compose.yml` file already has this environment variable set to `true` by default.

## Manual Generation

You can also generate the demo data manually by running the script directly:

```bash
# Navigate to the backend directory
cd backend

# Make sure Django environment is set up correctly
python manage.py shell

# Exit the shell
exit()

# Run the data generation script
python generate_demo_data.py
```

## Generated Data

The script will create:

1. **Users**:
   - Admin user: `admin@example.com` (password: admin123)
   - 80 customer accounts with randomized names
   - 10 moderator accounts
   - 40 business accounts

2. **Services**:
   - 73 services distributed among business accounts
   - Services are categorized into 14 different categories
   - Each business has at least one service

3. **Inquiries and Conversations**:
   - 100 inquiries from customers about services
   - Each inquiry includes messages between the customer, business, and sometimes a moderator
   - About 80% of inquiries are closed
   - Many closed inquiries include transactions and reviews

4. **Financial Data**:
   - All users have wallets with funds
   - Transactions between customers and businesses
   - Deposit transactions

## Customization

You can customize the amount of generated data by modifying the constants at the top of the `generate_demo_data.py` file:

```python
# Configuration
NUM_CUSTOMERS = 80
NUM_MODERATORS = 10
NUM_BUSINESSES = 40
NUM_SERVICES = 73
NUM_INQUIRIES = 100
NUM_CATEGORIES = 14
```

## Note

Running the script multiple times will create additional data - it doesn't replace existing data. The script avoids duplicates by checking for existing records and generating unique names/IDs as needed.

## Resetting the Database

### For Local Development

If you want to start with a clean database before generating demo data, you can reset your database:

```bash
# Reset the database
python manage.py flush

# Run migrations again
python manage.py migrate

# Generate the demo data
python generate_demo_data.py
```

### For Production/Deployment

When deploying with docker-compose.prod.yml, you can use environment variables to control database reset and demo data generation:

```bash
# To reset the database and generate demo data in one command:
RESET_DATABASE=true GENERATE_DEMO_DATA=true docker-compose -f docker-compose.prod.yml up -d

# To only reset the database:
RESET_DATABASE=true docker-compose -f docker-compose.prod.yml up -d

# To only generate demo data:
GENERATE_DEMO_DATA=true docker-compose -f docker-compose.prod.yml up -d
```

For Railway deployment, set these variables in your Railway project settings:

1. `RESET_DATABASE`: Set to "true" to clear all data (temporary)
2. `GENERATE_DEMO_DATA`: Set to "true" to generate demo data

**Important**: After the database has been reset and/or demo data has been generated, you should remove or set these environment variables back to "false" to prevent accidental data loss on subsequent deployments.