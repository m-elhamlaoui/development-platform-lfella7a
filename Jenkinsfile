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
                scriptpipeline {
    agent any
    
    environment {
        WILDFLY_HOME = '/path/to/wildfly/wildfly-36.0.0.Final' // Update this path
        PORT_OFFSET = '20000' // Using port offset as mentioned in your guide
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', // Changed from 'master' to 'main'
                    credentialsId: 'water_watch',
                    url: 'https://github.com/m-elhamlaoui/development-platform-lfella7a.git'
            }
        }
        
        stage('Build') {
            steps {
                // Maven build as described in your guide
                sh 'mvn clean package'
            }
        }
        
        stage('Deploy') {
            steps {
                // Deploy to WildFly using Maven plugin
                sh 'mvn wildfly:deploy'
                
                // Alternative: Manual deployment
                // sh "cp target/auth-backend.war ${WILDFLY_HOME}/standalone/deployments/"
            }
        }
        
        stage('Restart WildFly') {
            steps {
                // Stop WildFly if running
                sh "if pgrep -f 'java.*jboss'; then ${WILDFLY_HOME}/bin/jboss-cli.sh --connect command=:shutdown; fi"
                
                // Start WildFly with port offset
                sh "${WILDFLY_HOME}/bin/standalone.sh -Djboss.socket.binding.port-offset=${PORT_OFFSET} &"
                
                // Wait for WildFly to start
                sh 'sleep 30'
                
                // Verify deployment
                sh "curl -s http://localhost:28081/auth-backend | grep 'Jakarta EE Authentication Backend'"
            }
        }
        
        stage('Database Verification') {
            steps {
                // Verify database connection
                sh "psql -U postgres -d authdb -c 'SELECT COUNT(*) FROM users;'"
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
        }
    }
}