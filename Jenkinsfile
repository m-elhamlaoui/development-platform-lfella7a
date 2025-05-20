pipeline {
    agent any
    
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
                // Your build steps here
                echo 'Building the application...'
                // Add actual build commands for your project
            }
        }
        
        stage('Deploy') {
            steps {
                // Your deployment steps here
                echo 'Deploying the application...'
                // Add actual deployment commands
            }
        }
        
        stage('Restart WildFly') {
            steps {
                // Steps to restart WildFly
                echo 'Restarting WildFly server...'
                // Add actual WildFly restart commands
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline execution failed.'
        }
    }
}