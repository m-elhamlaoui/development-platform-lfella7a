# JEE Jakarta Authentication Backend

A robust Jakarta EE backend application providing user authentication functionality (sign up and sign in) using PostgreSQL for database storage and JWT for secure authentication.

## Features

- **User Registration**: Secure sign-up with email validation and password hashing
- **User Authentication**: Sign-in with JWT token generation
- **Database Storage**: PostgreSQL integration with JPA 
- **Web Interface**: Simple UI for testing the authentication flow
- **Security**: Password hashing and JWT token-based authentication

## Technologies Used

- Jakarta EE 10
- Jakarta Persistence (JPA)
- Jakarta RESTful Web Services (JAX-RS)
- Jakarta Context and Dependency Injection (CDI)
- Jakarta Security
- PostgreSQL 17
- JWT (JSON Web Tokens)
- WildFly 36.0.0.Final (Application Server)
- Maven (Build tool)

## Project Structure

The project follows a standard Maven structure with additional organization:

```
lostcity/
├── src/                    # Source code
├── docs/                   # Documentation
│   ├── README.md           # This file
│   ├── SETUP.md            # Environment setup instructions
│   ├── TECH.md             # Technical details and error solving strategies
│   └── RUN.md              # Deployment and execution instructions
├── config/                 # Configuration files
│   └── configure-postgres.cli
├── scripts/                # Utility scripts
│   ├── start-wildfly.bat
│   ├── setup-postgres.bat
│   ├── setup-wildfly.bat
│   └── configure-datasource.bat
├── lib/                    # External libraries
│   └── postgresql-42.7.2.jar
├── pom.xml                 # Maven project configuration
└── target/                 # Compiled output (generated)
```

## Quick Start

For detailed setup and deployment instructions, please refer to:

- [SETUP.md](SETUP.md) - Environment setup instructions
- [TECH.md](TECH.md) - Technical details and error solving strategies
- [RUN.md](RUN.md) - Deployment and execution instructions

## Database Access

You can access and view the database in several ways:

1. **Using pgAdmin 4**:
   - Connect to your local PostgreSQL server
   - Navigate to the `authdb` database
   - Expand Tables to see the `users` table
   - Right-click on the table and select "View/Edit Data" to see all records

2. **Using psql (Command Line)**:
   ```
   psql -U postgres -d authdb -c "SELECT * FROM users;"
   ```

3. **Using the Application API**:
   - The `/api/auth/signup` endpoint creates new users in the database
   - The `/api/auth/signin` endpoint authenticates users against the database

## REST API Endpoints

### User Registration
- **URL**: `/api/auth/signup`
- **Method**: POST
- **Request Body**: `{"username": "user123", "email": "user@example.com", "password": "password123"}`
- **Success Response**: 200 OK - `"User registered successfully!"`

### User Authentication
- **URL**: `/api/auth/signin`
- **Method**: POST
- **Request Body**: `{"username": "user123", "password": "password123"}`
- **Success Response**: 200 OK - `{"token": "JWT_TOKEN", "type": "Bearer", "id": 1, "username": "user123", "email": "user@example.com"}`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 