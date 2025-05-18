# Technical Details and Problem Solutions

This document provides technical details about the Jakarta EE authentication backend implementation and solutions to problems we encountered during development.

## Project Structure

The project follows a well-organized structure:

```
lostcity/
├── src/                    # Source code
├── docs/                   # Documentation
│   ├── README.md           # Project overview
│   ├── SETUP.md            # Environment setup instructions
│   ├── TECH.md             # Technical details (this file)
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

## Architecture Overview

The application follows a standard layered architecture:

1. **Presentation Layer** (JAX-RS REST Controllers)
   - Handles HTTP requests/responses
   - Performs basic validation
   - Delegates to service layer

2. **Service Layer**
   - Contains business logic
   - Manages transactions
   - Performs authentication and token generation

3. **Data Access Layer**
   - JPA entities
   - Repository classes for database operations
   - Manages database connections

4. **Security Layer**
   - JWT token generation and validation
   - Password hashing implementation
   - Security utilities

## Key Technical Challenges and Solutions

### 1. CDI Ambiguous Dependency Issue

**Problem:** Upon deployment, we encountered an ambiguous dependency injection issue with the `Pbkdf2PasswordHash` interface:

```
org.jboss.weld.exceptions.DeploymentException: WELD-001409: Ambiguous dependencies for type Pbkdf2PasswordHash with qualifiers @Default
```

**Solution:** We redesigned the `PasswordHashProducer` class to use an anonymous inner class implementation rather than a named static class:

```java
@Produces
@ApplicationScoped
public Pbkdf2PasswordHash createPasswordHash() {
    // Anonymous inner class implementation to avoid CDI ambiguity
    return new Pbkdf2PasswordHash() {
        // Implementation details...
    };
}
```

This approach ensures that CDI only has one implementation of the interface available for injection.

### 2. Database Schema Mapping Issues

**Problem:** We encountered issues with JPA entity mapping to the existing database schema:

```
Error: null value in column "password_hash" of relation "users" violates not-null constraint
```

**Solution:** We updated the User entity to match the exact schema of the database:

1. Added the `@Column(name = "password_hash")` annotation to map the field correctly
2. Added a `salt` field required by the database
3. Added a separate `password` field to match the database schema

```java
@Column(name = "password_hash", nullable = false)
private String passwordHash;

@Column(nullable = false)
private String salt;

@Column(nullable = false)
private String password;
```

### 3. JWT Token Security Issue

**Problem:** When testing the signin endpoint, we encountered this error:

```
Error: The signing key's size is 456 bits which is not secure enough for the HS512 algorithm. 
The JWT JWA Specification (RFC 7518, Section 3.2) states that keys used with HS512 MUST have 
a size >= 512 bits.
```

**Solution:** We implemented a more secure approach for JWT signing key generation using Base64-encoded secrets:

```java
private static final String JWT_SECRET = "bXlTdXBlclNlY3VyZUFuZFZlcnlMb25nU2VjcmV0S2V5Rm9yU2lnbmluZ0pXVFRva2Vuc0luSmFrYXJ0YUVFQXV0aEJhY2tlbmRBcHBsaWNhdGlvbg==";

@PostConstruct
public void init() {
    byte[] keyBytes = Base64.getDecoder().decode(JWT_SECRET);
    signingKey = Keys.hmacShaKeyFor(keyBytes);
}
```

This ensures the key has sufficient entropy for the HS512 algorithm.

### 4. WildFly Port Conflicts

**Problem:** During deployment, WildFly failed to start with port binding errors:

```
Failed to start service org.wildfly.undertow.listener.default: Address already in use: bind /127.0.0.1:8081
```

**Solution:** We configured WildFly to start with a port offset to avoid conflicts with other services in our `scripts/start-wildfly.bat`:

```
start "WildFly Server" standalone.bat -Djboss.socket.binding.port-offset=20000
```

This changed the ports to:
- HTTP: 28081 (8081 + 20000)
- HTTPS: 28443 (8443 + 20000)
- Management: 29990 (9990 + 20000)

### 5. PostgreSQL Connection Configuration

**Problem:** The application couldn't connect to the PostgreSQL database due to authentication issues.

**Solution:** We implemented several fixes:
1. Created the `scripts/setup-wildfly.bat` to configure PostgreSQL module in WildFly
2. Added the JDBC driver to the `lib` directory
3. Created `scripts/configure-datasource.bat` to configure the datasource in WildFly:

```xml
<datasource jndi-name="java:/jdbc/AuthDB" pool-name="AuthDS" enabled="true" use-java-context="true">
    <connection-url>jdbc:postgresql://localhost:5432/authdb</connection-url>
    <driver>postgresql</driver>
    <security>
        <user-name>postgres</user-name>
        <password>postgres</password>
    </security>
</datasource>
```

### 6. CORS Configuration for Authenticated Requests

**Problem:** We encountered CORS errors when the frontend tried to make authenticated requests to the backend:

```
Access to XMLHttpRequest at 'http://localhost:28081/auth-backend/api/auth/signin' from origin 'http://localhost:3000' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: The value of the 'Access-Control-Allow-Origin' header in the response must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**Solution:** We implemented a proper CORS filter:

1. Created a `CORSFilter` class that implements `ContainerResponseFilter`
2. Used specific origin configuration instead of wildcard:

```java
@Provider
public class CORSFilter implements ContainerResponseFilter {
    @Override
    public void filter(ContainerRequestContext requestContext, ContainerResponseContext responseContext) throws IOException {
        // Allow requests from the frontend origin
        responseContext.getHeaders().add("Access-Control-Allow-Origin", "http://localhost:3000");
        
        // Allow specific HTTP methods
        responseContext.getHeaders().add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        
        // Allow specific headers
        responseContext.getHeaders().add("Access-Control-Allow-Headers", "Content-Type, Authorization");
        
        // Allow credentials
        responseContext.getHeaders().add("Access-Control-Allow-Credentials", "true");
        
        // Set max age for preflight requests
        responseContext.getHeaders().add("Access-Control-Max-Age", "3600");
    }
}
```

3. Modified the frontend API client to include `credentials: 'include'` in fetch requests

### 7. JSON Response Format Issue

**Problem:** The frontend received "Unexpected token" errors when parsing response data from the backend:

```
SyntaxError: Unexpected token 'U', "User regis"... is not valid JSON
```

**Solution:**
1. Updated all API endpoints to return properly formatted JSON with appropriate content type:

```java
return Response.ok("{\"message\": \"User registered successfully!\"}")
    .type(MediaType.APPLICATION_JSON)
    .build();
```

2. Used proper JSON error responses for consistent handling:

```java
return Response.status(Response.Status.UNAUTHORIZED)
    .entity("{\"error\": \"Invalid username or password!\"}")
    .type(MediaType.APPLICATION_JSON)
    .build();
```

### 8. JWT Token Claims Enhancement

**Problem:** The JWT token didn't include enough user information, causing the dashboard to display incomplete data:

```
Welcome back, ! // Missing username
```

**Solution:** Enhanced the JWT token generation to include additional claims with user information:

```java
return Jwts.builder()
    .setSubject(user.getUsername())
    .claim("id", user.getId())
    .claim("email", user.getEmail())
    .claim("username", user.getUsername())
    .setIssuedAt(new Date())
    .setExpiration(new Date((new Date()).getTime() + JWT_EXPIRATION_MS))
    .signWith(getSigningKey(), SignatureAlgorithm.HS512)
    .compact();
```

This ensured the frontend could extract the complete user profile from the token.

## Database Management

### 1. Database Schema

The `users` table schema:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 2. Accessing and Managing the Database

#### Using pgAdmin 4

1. **Connect to your PostgreSQL server**:
   - Host: localhost
   - Port: 5432
   - Username: postgres
   - Password: [your password]

2. **Navigating the database**:
   - Expand Servers → your server → Databases → authdb → Schemas → public → Tables
   - You'll see the `users` table

3. **View and edit data**:
   - Right-click on `users` and select "View/Edit Data" → "All Rows"
   - You can add/edit/delete records directly in the data grid

4. **Running custom queries**:
   - Click the Query Tool button (lightning bolt icon)
   - Enter SQL commands like `SELECT * FROM users;`
   - Click Execute/Refresh to run the query

#### Using Command Line (psql)

```bash
# View all users
psql -U postgres -d authdb -c "SELECT * FROM users;"

# Add a test user
psql -U postgres -d authdb -c "INSERT INTO users (username, email, password_hash, salt, password, created_at, updated_at) VALUES ('testuser', 'test@example.com', 'hashedpassword123', 'testsalt123', 'N/A', NOW(), NOW());"

# Delete a user
psql -U postgres -d authdb -c "DELETE FROM users WHERE username = 'testuser';"
```

## Performance Considerations

1. **Connection Pooling**: The datasource is configured with connection pooling to minimize database connection overhead.

2. **JWT Verification**: JWT token validation is optimized to quickly verify tokens without excessive cryptographic operations.

3. **Password Hashing**: We use SHA-256 with salt for password hashing, which provides a good balance between security and performance.

## Security Considerations

1. **Password Storage**: 
   - Passwords are never stored in plain text
   - We use salted hashing to prevent rainbow table attacks
   
2. **JWT Security**:
   - Tokens expire after 24 hours by default
   - Tokens are signed with a strong key using HS512 algorithm
   
3. **Input Validation**:
   - All user inputs are validated before processing
   - JPA parameterized queries protect against SQL injection

## Future Improvements

1. **Implement Password Policies**: Enforce stronger password requirements
2. **Add Token Refresh Mechanism**: Implement token refresh to extend sessions without re-authentication
3. **Rate Limiting**: Add protection against brute-force attacks
4. **Role-Based Access Control**: Extend the security model to include user roles and permissions 