pipeline {
    agent any

    environment {
        WILDFLY_HOME = '/path/to/your/wildfly'
        MAVEN_HOME = '/usr/share/maven'
        JAVA_HOME = '/usr/lib/jvm/java-17-openjdk-amd64'
    }

    stages {
        stage('Checkout') {
            steps {
                git credentialsId: 'water_watch', url: 'https://github.com/m-elhamlaoui/development-platform-lfella7a.git'
            }
        }

        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }

        stage('Deploy') {
            steps {
                sh 'cp target/auth-backend.war $WILDFLY_HOME/standalone/deployments/'
            }
        }

        stage('Restart WildFly') {
            steps {
                sh '$WILDFLY_HOME/bin/jboss-cli.sh --connect --command=":reload"'
            }
        }
    }
}
