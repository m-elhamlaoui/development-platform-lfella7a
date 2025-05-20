pipeline {
    agent any
    
    environment {
        // Update paths based on your Jenkins server configuration
        JAVA_HOME = tool 'JDK17'
        MAVEN_HOME = tool 'Maven3'
        WILDFLY_DIR = 'backend/wildfly/wildfly-36.0.0.Final'
        PATH = "${JAVA_HOME}/bin:${MAVEN_HOME}/bin:${env.PATH}"
        
        // Database configuration
        DB_HOST = 'localhost'
        DB_NAME = 'authdb'
        DB_USER = credentials('postgres-user')
        DB_PASS = credentials('postgres-password')
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'water_watch',
                    url: 'https://github.com/m-elhamlaoui/development-platform-lfella7a.git'
            }
        }
        
        stage('Setup Backend') {
            steps {
                // Check if WildFly is already set up
                script {
                    def wildflyExists = fileExists("${WILDFLY_DIR}/bin/standalone.sh")
                    if (!wildflyExists) {
                        // Run the setup script if WildFly doesn't exist
                        sh './setup-backend.bat'
                    } else {
                        echo "WildFly is already set up. Skipping setup."
                    }
                }
            }
        }
        
        stage('Build') {
            steps {
                dir('backend') {
                    // Build using Maven
                    sh 'mvn clean package'
                }
            }
        }
        
        stage('Deploy') {
            steps {
                // Stop WildFly if running
                sh "if pgrep -f 'java.*jboss'; then ${WILDFLY_DIR}/bin/jboss-cli.sh --connect command=:shutdown; fi || true"
                
                // Deploy using the script
                sh './deploy-backend.bat'
                
                // Alternatively, deploy manually
                // sh "cp backend/target/auth-backend.war ${WILDFLY_DIR}/standalone/deployments/"
            }
        }
        
        stage('Verify Deployment') {
            steps {
                // Wait for deployment to complete
                sleep time: 30, unit: 'SECONDS'
                
                // Verify the application is running
                sh 'curl -s http://localhost:28081/auth-backend | grep "Jakarta EE Authentication Backend" || echo "Application not responding"'
                
                // Verify database connection
                script {
                    // Using the PostgreSQL JDBC driver for a simple connection test
                    sh """
                    echo "
                    import java.sql.Connection;
                    import java.sql.DriverManager;
                    
                    public class DBTest {
                        public static void main(String[] args) {
                            try {
                                Connection conn = DriverManager.getConnection(
                                    \"jdbc:postgresql://${DB_HOST}:5432/${DB_NAME}\", 
                                    \"${DB_USER}\", 
                                    \"${DB_PASS}\"
                                );
                                System.out.println(\"Database connection successful\");
                                conn.close();
                            } catch (Exception e) {
                                System.out.println(\"Database connection failed: \" + e.getMessage());
                                System.exit(1);
                            }
                        }
                    }
                    " > DBTest.java
                    javac -cp backend/lib/postgresql-42.6.0.jar DBTest.java
                    java -cp .:backend/lib/postgresql-42.6.0.jar DBTest
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline executed successfully!'
            echo 'The application is now available at: http://localhost:28081/auth-backend'
        }
        failure {
            echo 'Pipeline execution failed.'
            echo 'Check the logs for more information.'
            
            // Try to collect logs for debugging
            sh "if [ -f ${WILDFLY_DIR}/standalone/log/server.log ]; then tail -n 100 ${WILDFLY_DIR}/standalone/log/server.log; fi || true"
        }
        always {
            // Clean up temporary files
            sh 'rm -f DBTest.java DBTest.class || true'
        }
    }
}