pipeline {
    agent any

    environment {
        MAVEN_HOME = '/opt/maven'          // Adjust if your Maven is installed elsewhere
        JAVA_HOME = '/usr/lib/jvm/java-17-openjdk-amd64' // Adjust for JDK 17
        PATH = "${MAVEN_HOME}/bin:${JAVA_HOME}/bin:$PATH"
    }

    tools {
        maven 'Maven 3.8'   // Ensure Jenkins has this tool configured in Global Tools
        jdk 'JDK 17'        // Also configure JDK 17 in Jenkins
    }

    options {
        skipStagesAfterUnstable()
    }

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'git@github.com:m-elhamlaoui/development-platform-lfella7a.git'
            }
        }

        stage('Build WAR') {
            steps {
                dir('backend') {
                    sh 'mvn clean package'
                }
            }
        }

        stage('Deploy to WildFly') {
            steps {
                script {
                    // Make sure WildFly is already running and management user is configured
                    def wildfly_cli = '/opt/wildfly/bin/jboss-cli.sh' // adjust as needed

                    sh """
                        ${wildfly_cli} --connect --command="deploy backend/target/auth-backend.war --force"
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ Deployment succeeded!'
        }
        failure {
            echo '❌ Deployment failed. Check logs.'
        }
    }
}
