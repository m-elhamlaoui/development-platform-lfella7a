# Setting up WildFly with PostgreSQL for the Auth Backend

## Prerequisites
1. JDK 17 or higher
2. PostgreSQL 17 or higher installed and added to PATH
3. WildFly 36.0.0.Final (included in the project)

## Automated Setup Process

We've provided batch scripts to automate the setup process. You can either:

### Option 1: Run the Complete Setup Script

Run the all-in-one setup script:
```
scripts\setup.bat
```

This script executes all setup steps in sequence:
1. Creates the PostgreSQL database
2. Configures the WildFly server
3. Starts WildFly
4. Sets up the datasource

### Option 2: Run Individual Setup Scripts

If you prefer to run each step individually:

#### 1. PostgreSQL Setup
First, ensure PostgreSQL is running and set the password for the postgres user:

```sql
-- Run in PostgreSQL's psql console
ALTER USER postgres WITH PASSWORD 'postgres';
```

Then run the setup script:
```
scripts\setup-postgres.bat
```

This will create the `authdb` database.

#### 2. WildFly Setup
Run the WildFly setup script:
```
scripts\setup-wildfly.bat
```

This sets up the PostgreSQL module in WildFly and copies the necessary JDBC driver.

#### 3. Start WildFly
Start the WildFly server with port offset to avoid conflicts:
```
scripts\start-wildfly.bat
```

This will start WildFly with a port offset of 20000, resulting in:
- HTTP port: 28081 (default 8081 + 20000)
- HTTPS port: 28443 (default 8443 + 20000)
- Management port: 29990 (default 9990 + 20000)

#### 4. Configure PostgreSQL Datasource
Run the datasource configuration script:
```
scripts\configure-datasource.bat
```

This creates the necessary datasource in WildFly. You can verify it in the admin console:
http://localhost:29990

## Building and Deploying the Application

### Option 1: Use the Deployment Script
```
scripts\deploy.bat
```

This script builds and deploys the application in one step.

### Option 2: Manual Build and Deploy
1. Build the application:
   ```
   mvn clean package
   ```

2. Deploy the application:
   ```
   mvn wildfly:deploy
   ```
   
   Or manually deploy the WAR file by copying it to:
   ```
   wildfly\wildfly-36.0.0.Final\standalone\deployments\
   ```

3. Access the application at:
   ```
   http://localhost:28081/auth-backend
   ```

## API Endpoints
- Sign up: `POST /api/auth/signup`
- Sign in: `POST /api/auth/signin`

## Troubleshooting

### PostgreSQL Connection Issues
If you encounter errors like:
```
FATAL: password authentication failed for user "postgres"
```

Try these steps:
1. Ensure PostgreSQL is running
2. Reset the postgres user password:
   ```sql
   -- In psql console after connecting as a superuser:
   ALTER USER postgres WITH PASSWORD 'postgres';
   ```
3. Check pg_hba.conf file to ensure it allows password authentication for local connections

### WildFly Issues
If the datasource connection fails:
1. Verify WildFly is running (check http://localhost:29990 admin console)
2. Ensure PostgreSQL module was created correctly in:
   ```
   wildfly\wildfly-36.0.0.Final\modules\org\postgresql\main\
   ```
3. Verify the JDBC driver was copied from the `lib` directory
4. Check WildFly logs at `wildfly\wildfly-36.0.0.Final\standalone\log\server.log` 