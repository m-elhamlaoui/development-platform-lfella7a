# Jakarta EE Authentication Backend

This is a Jakarta EE backend application that provides user authentication functionality using PostgreSQL and JWT tokens.

## Documentation

All project documentation is available in the `docs` folder:

- [Main Documentation](docs/README.md) - Overview and features
- [Setup Guide](docs/SETUP.md) - Environment setup instructions
- [Technical Details](docs/TECH.md) - Technical information and problem solutions
- [Deployment Guide](docs/RUN.md) - Instructions for deploying and running the application

## Project Structure

The project is organized as follows:

```
lostcity/
├── src/                    # Source code
├── docs/                   # Documentation
├── config/                 # Configuration files
├── scripts/                # Utility scripts
│   ├── setup.bat           # Complete environment setup
│   ├── deploy.bat          # Build and deployment
│   ├── start-wildfly.bat   # Start WildFly server
│   ├── setup-postgres.bat  # Database setup
│   ├── setup-wildfly.bat   # WildFly configuration
│   └── configure-datasource.bat # Datasource configuration
├── lib/                    # External libraries
├── pom.xml                 # Maven project configuration
└── target/                 # Compiled output (generated)
```

## Quick Start

### Using Automation Scripts

We've provided convenience scripts to simplify the setup and deployment process:

1. **Complete setup**: Run `scripts\setup.bat` to automatically:
   - Create the PostgreSQL database
   - Configure WildFly
   - Start the WildFly server
   - Configure the datasource

2. **Build and deploy**: Run `scripts\deploy.bat` to:
   - Build the application
   - Deploy it to WildFly

### Manual Setup

If you prefer to run each step manually:

1. Set up the environment - see [Setup Guide](docs/SETUP.md)
2. Build the application with `mvn clean package`
3. Deploy using `mvn wildfly:deploy`
4. Access the application at `http://localhost:28081/auth-backend`

For detailed instructions, please refer to the documentation in the `docs` folder. 