pipeline {
    agent any

    tools {
        maven 'Maven 3.8'   // Make sure this matches what you configured in Jenkins Global Tools
        jdk 'JDK 17'
    }

    environment {
        WILDFLY_CLI = '/opt/wildfly/bin/jboss-cli.sh'  // Adjust this path if needed
    }

    stages {
        stage('Clone') {
            steps {
                git branch: 'main',
                    url: 'git@github.com:m-elhamlaoui/development-platform-lfella7a.git'
            }
        }

        stage('Build') {
            steps {
                dir('backend') {
                    sh 'mvn clean package'
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('backend') {
                    sh '${WILDFLY_CLI} --connect --command="deploy target/auth-backend.war --force"'
                }
            }
        }
    }

    post {
        success {
            echo '✅ Build and deployment completed successfully.'
        }
        failure {
            echo '❌ Build or deployment failed. Check the console output.'
        }
    }
}
