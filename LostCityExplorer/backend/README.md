# Backend Development Guide - Jakarta EE

This directory contains the backend service for the Lost City Explorer application, built with Jakarta EE.

## Setup Instructions

### Prerequisites

- JDK 11 or later
- Maven 3.6+
- Docker (for local development)
- An IDE (Eclipse, IntelliJ IDEA, etc.)

### Project Setup

1. Initialize a new Jakarta EE project:

```bash
mvn archetype:generate -DarchetypeGroupId=org.apache.maven.archetypes -DarchetypeArtifactId=maven-archetype-webapp -DgroupId=com.lostcityexplorer -DartifactId=backend -Dversion=1.0.0
```

2. Add Jakarta EE dependencies to your `pom.xml`:

```xml
<dependencies>
    <!-- Jakarta EE API -->
    <dependency>
        <groupId>jakarta.platform</groupId>
        <artifactId>jakarta.jakartaee-api</artifactId>
        <version>9.1.0</version>
        <scope>provided</scope>
    </dependency>
    
    <!-- Jakarta Security -->
    <dependency>
        <groupId>jakarta.security.enterprise</groupId>
        <artifactId>jakarta.security.enterprise-api</artifactId>
        <version>2.0.0</version>
        <scope>provided</scope>
    </dependency>
    
    <!-- PostgreSQL JDBC Driver -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <version>42.6.0</version>
    </dependency>
</dependencies>
```

3. Organize your project structure:

```
backend/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── lostcityexplorer/
│   │   │           ├── config/        # App configuration
│   │   │           ├── controllers/   # REST endpoints
│   │   │           ├── models/        # Data models
│   │   │           ├── repositories/  # Data access
│   │   │           └── services/      # Business logic
│   │   ├── resources/                 # Configuration files
│   │   └── webapp/                    # Web resources
│   └── test/                          # Unit tests
├── pom.xml                            # Maven configuration
└── Dockerfile                         # Docker configuration
```

### Key Implementation Tasks

1. Implement REST API controllers for:
   - Authentication and user management
   - Satellite data search and retrieval
   - Metadata management
   - Image processing requests

2. Set up data models for:
   - User accounts
   - Satellite imagery metadata
   - Location markers and annotations

3. Configure Jakarta Security for:
   - User authentication
   - OAuth2 integration
   - API endpoint security

4. Implement database access using JPA:
   - Entity mapping for PostgreSQL
   - Repository pattern implementation
   - Transaction management

### Docker Development

The Dockerfile is already configured to use Payara Server. To build and run:

```bash
docker build -t lostcity-backend .
docker run -p 8080:8080 lostcity-backend
```

Or use the provided docker-compose.yml from the root directory:

```bash
cd ..
docker-compose up -d
```

This will start the backend service along with the database and other components.

### Health Check Endpoint

Implement a health check endpoint at `/health` to facilitate container orchestration:

```java
@Path("/health")
public class HealthResource {
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response healthCheck() {
        return Response.ok(Map.of("status", "UP")).build();
    }
}
```

### API Documentation

Consider using Swagger/OpenAPI to document your endpoints:

```xml
<dependency>
    <groupId>org.eclipse.microprofile.openapi</groupId>
    <artifactId>microprofile-openapi-api</artifactId>
    <version>2.0</version>
</dependency>
```

Access the API documentation at `/openapi` once implemented.

## Integration Points

The backend will need to interact with:
- The ML/AI service for image analysis (available at `http://ml_ai:5000`)
- The GIS Tools service for spatial analysis (available at `http://gis_tools:3001`)
- The frontend application that consumes the APIs

## Additional Resources

- [Jakarta EE Documentation](https://jakarta.ee/specifications/platform/9.1/)
- [Jakarta Security Documentation](https://jakarta.ee/specifications/security/2.0/)
- [Payara Server Documentation](https://docs.payara.fish/) 