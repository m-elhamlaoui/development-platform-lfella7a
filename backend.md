# Lost City App - Backend Documentation

## Overview

The Lost City App backend is a robust Jakarta EE application that provides authentication and data management services. It's built using modern enterprise Java technologies and follows best practices for scalability, security, and maintainability.

## Technologies Used

### Core Framework
- **Jakarta EE 10.0.0** - Enterprise Java platform providing comprehensive APIs for building enterprise applications
- **JAX-RS** - RESTful web services framework for building HTTP-based APIs
- **CDI (Contexts and Dependency Injection)** - Dependency injection and contextual lifecycle management
- **Bean Validation** - Data validation using annotations

### Application Server
- **WildFly 36.0.0.Final** - Open-source application server that implements Jakarta EE specifications
- **Port Configuration**: Uses port offset of 20000 for development
  - HTTP: `http://localhost:28080`
  - Management Console: `http://localhost:29990`
  - Application: `http://localhost:28080/auth-backend`

### Database & Persistence
- **PostgreSQL** - Open-source relational database
- **Hibernate ORM 6.2.7.Final** - Object-relational mapping framework
- **HikariCP 5.0.1** - High-performance JDBC connection pool
- **Jakarta Persistence API (JPA)** - Java persistence specification

### Security & Authentication
- **JWT (JSON Web Tokens)** - Token-based authentication using JJWT library (0.11.5)
- **Custom Security Filters** - Request authentication and authorization
- **Password Hashing** - Secure password storage

### Development Tools
- **Maven** - Build automation and dependency management
- **Java 17** - Programming language and runtime
- **Hibernate Validator 8.0.1.Final** - Bean validation implementation

## Architecture

The backend follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│           REST Controllers          │  ← JAX-RS endpoints
├─────────────────────────────────────┤
│              Services               │  ← Business logic layer
├─────────────────────────────────────┤
│            Repositories             │  ← Data access layer
├─────────────────────────────────────┤
│              Entities               │  ← JPA entities
└─────────────────────────────────────┘
```

### Package Structure
```
com.auth.backend/
├── controller/     # REST API endpoints
├── service/        # Business logic services
├── repository/     # Data access objects
├── entity/         # JPA entities
├── dto/           # Data transfer objects
├── security/      # Security components
└── filter/        # HTTP filters
```

## How to Run the Server

### Prerequisites
- Java 17 or higher
- PostgreSQL database
- Maven 3.6+

### Method 1: Automated Setup (Recommended)

1. **Complete Environment Setup**
   ```bash
   setup-backend.bat
   ```
   This script will:
   - Set up PostgreSQL database
   - Configure WildFly server
   - Start the application server
   - Configure datasources

2. **Start WildFly Server**
   ```bash
   start-wildfly-server.bat
   ```

### Method 2: Manual Setup

1. **Database Setup**
   ```bash
   cd backend
   scripts\setup-postgres.bat
   ```

2. **WildFly Configuration**
   ```bash
   scripts\setup-wildfly.bat
   ```

3. **Start WildFly Server**
   ```bash
   scripts\start-wildfly.bat
   ```

4. **Configure Datasource**
   ```bash
   scripts\configure-datasource.bat
   ```

5. **Build and Deploy Application**
   ```bash
   mvn clean package
   scripts\deploy.bat
   ```

### Method 3: Maven Profile Deployment

```bash
cd backend
mvn clean package wildfly:deploy -Pwildfly
```

## Server Management

### WildFly Management Console
- **URL**: `http://localhost:29990/console/index.html`
- **Username**: `admini`
- **Password**: `admini`

The management console allows you to:
- Monitor server status and performance
- Manage deployments
- Configure datasources
- View server logs
- Manage security settings

### Application Endpoints
- **Base URL**: `http://localhost:28080/auth-backend`
- **Health Check**: `http://localhost:28080/auth-backend/api/health`
- **API Documentation**: Available through the management console

## Configuration Files

### Maven Configuration (`pom.xml`)
- Defines project dependencies
- Configures build plugins
- Sets up WildFly deployment profile

### WildFly Configuration
- **Location**: `backend/wildfly/wildfly-36.0.0.Final/standalone/configuration/`
- **Main Config**: `standalone.xml`
- **Management Users**: `mgmt-users.properties`
- **Application Users**: `application-users.properties`

### Database Configuration
- **JDBC URL**: Configured in WildFly datasource
- **Connection Pool**: HikariCP with optimized settings
- **Driver**: PostgreSQL JDBC driver (42.6.0)

## Development Workflow

1. **Make Code Changes**
   - Edit source files in `src/main/java/`
   - Update resources in `src/main/resources/`

2. **Build Application**
   ```bash
   mvn clean compile
   ```

3. **Run Tests**
   ```bash
   mvn test
   ```

4. **Package and Deploy**
   ```bash
   mvn clean package
   scripts\deploy.bat
   ```

5. **Hot Deployment**
   - WildFly supports hot deployment
   - Simply copy the WAR file to `deployments/` directory

## Monitoring and Logs

### Server Logs
- **Location**: `backend/wildfly/wildfly-36.0.0.Final/standalone/log/`
- **Main Log**: `server.log`
- **Access Log**: Available through configuration

### Application Monitoring
- Use WildFly management console for real-time monitoring
- JVM metrics and performance data available
- Database connection pool statistics

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill existing Java processes
   taskkill /F /IM java.exe
   ```

2. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check datasource configuration in WildFly
   - Verify database credentials

3. **Deployment Failures**
   - Check server logs for detailed error messages
   - Ensure all dependencies are available
   - Verify WAR file is properly built

### Useful Commands

```bash
# Check if WildFly is running
tasklist | findstr java

# Check port usage
netstat -an | findstr :29990

# View WildFly processes
wmic process where "name='java.exe'" get commandline

# Restart WildFly
taskkill /F /IM java.exe
start-wildfly-server.bat
```

## Security Considerations

- JWT tokens for stateless authentication
- Secure password hashing
- CORS configuration for cross-origin requests
- Input validation using Bean Validation
- SQL injection prevention through JPA/Hibernate

## Performance Optimizations

- HikariCP connection pooling for database efficiency
- JPA second-level caching
- Optimized JVM settings in WildFly
- Efficient query design with Hibernate

## API Documentation

The backend provides RESTful APIs for:
- User authentication and authorization
- Data management operations
- Health checks and monitoring
- Administrative functions

For detailed API documentation, access the management console or refer to the controller classes in the source code. 