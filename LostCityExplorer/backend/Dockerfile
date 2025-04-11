FROM payara/server-full:latest

# Set the working directory
WORKDIR /opt/payara/deployments

# Copy the WAR file to the deployments directory
COPY target/*.war .

# Expose the port the application will run on
EXPOSE 8080

# Command to run the application
CMD ["asadmin", "start-domain", "-v"] 