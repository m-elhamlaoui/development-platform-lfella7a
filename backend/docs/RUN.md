# Deployment and Execution Guide

This document provides detailed instructions for deploying and running the Jakarta EE Authentication Backend.

## Prerequisites

Ensure you have completed all steps in [SETUP.md](SETUP.md) before proceeding:
- PostgreSQL 17 installed and configured
- WildFly 36.0.0.Final installed and configured
- JDK 17 or higher installed

## Building and Deploying the Application

### Option 1: Using the Deployment Script (Recommended)

The simplest way to build and deploy the application is to use our deployment script:

```bash
scripts\deploy.bat
```

This single script will:
1. Build the application using Maven
2. Deploy it to the WildFly server
3. Provide feedback on success or errors

### Option 2: Manual Process

#### Building the Application

1. Navigate to the project root directory
2. Build the application using Maven:
   ```bash
   mvn clean package
   ```
3. This will generate a WAR file in the `target` directory named `auth-backend.war`

#### Deploying to WildFly

##### Method 1: Using Maven Plugin

1. Deploy directly using the WildFly Maven plugin:
   ```bash
   mvn wildfly:deploy
   ```

2. To undeploy:
   ```bash
   mvn wildfly:undeploy
   ```

##### Method 2: Manual Deployment

1. Copy the WAR file to WildFly's deployments directory:
   ```bash
   copy target\auth-backend.war wildfly\wildfly-36.0.0.Final\standalone\deployments\
   ```

2. WildFly will automatically detect and deploy the application
3. Check the deployment status by looking for a file named `auth-backend.war.deployed` in the deployments directory

## Starting the Application Server

1. Start WildFly with the port offset to avoid conflicts using our script:
   ```bash
   scripts\start-wildfly.bat
   ```

2. Verify the server is running by visiting:
   - Admin Console: http://localhost:29990
   - Application URL: http://localhost:28081/auth-backend

## Accessing the Application

### Web Interface

A simple web interface is available at:
```
http://localhost:28081/auth-backend
```

### REST API Endpoints

You can use tools like Postman, cURL, or any HTTP client to interact with the API:

#### User Registration
```
POST http://localhost:28081/auth-backend/api/auth/signup
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123"
}
```

#### User Authentication
```
POST http://localhost:28081/auth-backend/api/auth/signin
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

## Database Access and Management

You can manage and monitor the database using several approaches:

### Using pgAdmin 4

1. Launch pgAdmin 4
2. Connect to your PostgreSQL server:
   - Host: localhost
   - Port: 5432
   - Username: postgres
   - Password: [your PostgreSQL password]

3. Navigate to:
   - Servers → [Your server] → Databases → authdb → Schemas → public → Tables → users

4. View the data:
   - Right-click on "users" table
   - Select "View/Edit Data" → "All Rows"

### Using psql (Command Line)

```bash
# View all registered users
psql -U postgres -d authdb -c "SELECT * FROM users;"

# View user count
psql -U postgres -d authdb -c "SELECT COUNT(*) FROM users;"

# Add a test user (for testing purposes)
psql -U postgres -d authdb -c "INSERT INTO users (username, email, password_hash, salt, password, created_at, updated_at) VALUES ('testuser', 'test@example.com', 'hashedpassword123', 'testsalt123', 'N/A', NOW(), NOW());"
```

## Logging and Monitoring

### Application Logs

WildFly server logs can be found at:
```
wildfly\wildfly-36.0.0.Final\standalone\log\server.log
```

### Database Logs

PostgreSQL logs are typically located at:
```
[PostgreSQL installation directory]\data\log\
```

## Troubleshooting

### Application Not Starting

1. Check WildFly logs for errors
2. Verify port availability (no conflicts)
3. Ensure database is running and accessible

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   psql -U postgres -c "SELECT 1;"
   ```

2. Check database connection parameters in:
   - src/main/resources/META-INF/persistence.xml
   - WildFly datasource configuration (configured by scripts\configure-datasource.bat)

### CORS Issues

If you encounter CORS errors from the frontend application, check:

1. Ensure the frontend is running on http://localhost:3000, which is the allowed origin in the CORS filter
2. Verify the CORSFilter class is properly deployed
3. Check that frontend requests include the proper credentials setting:
   ```typescript
   credentials: 'include'
   ```
4. Important: If you're using credentials (cookies, headers), the backend CORS filter must specify the exact origin, not a wildcard (*) for Access-Control-Allow-Origin

### JWT Token Issues

If authentication works but user information is not displayed correctly:

1. Check the JWT token is properly generated with user claims in JwtUtils.java
2. Examine JWT payload in the browser (localStorage) to ensure it contains id, username and email claims
3. Verify the frontend correctly extracts and uses these claims from the token

### Deployment Failures

1. Check for deployment errors in WildFly logs
2. Verify the WAR file is correctly built
3. Confirm JDK compatibility (JDK 17+)

## Frontend Integration

The authentication backend is designed to work with a Next.js frontend application running on http://localhost:3000. The key integration points are:

1. API endpoints:
   - POST `/api/auth/signup` - User registration
   - POST `/api/auth/signin` - User authentication

2. Authentication flow:
   - Frontend sends credentials to backend
   - Backend validates credentials and returns JWT token with user data claims
   - Frontend stores token in localStorage
   - Frontend includes token in subsequent requests

3. CORS configuration:
   - Backend CORSFilter configured to allow the frontend origin
   - Frontend uses credentials mode for cross-origin requests
   - All responses include the appropriate Content-Type headers (application/json)

## Restarting the Application

To restart the application after making changes:

1. Undeploy the existing application:
   ```bash
   mvn wildfly:undeploy
   ```

2. Rebuild and redeploy:
   ```bash
   mvn clean package wildfly:deploy
   ```
   
   Or simply run:
   ```bash
   scripts\deploy.bat
   ``` 