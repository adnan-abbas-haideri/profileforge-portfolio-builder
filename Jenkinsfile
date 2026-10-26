pipeline {
    agent any
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    environment {
        IMAGE_NAME = 'profileforge'
        DOCKERHUB_REPOSITORY = 'YOUR_DOCKERHUB_USERNAME/profileforge'
    }
    parameters {
        booleanParam(name: 'PUSH_IMAGE', defaultValue: false, description: 'Push the image to Docker Hub; configure DockerHubCred first')
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m unittest discover -s tests -v
                '''
            }
        }
        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                    docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest
                '''
            }
        }
        stage('Push to Docker Hub') {
            when { expression { return params.PUSH_IMAGE } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'DockerHubCred', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_TOKEN')]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKERHUB_REPOSITORY}:${BUILD_NUMBER}
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKERHUB_REPOSITORY}:latest
                        docker push ${DOCKERHUB_REPOSITORY}:${BUILD_NUMBER}
                        docker push ${DOCKERHUB_REPOSITORY}:latest
                        docker logout
                    '''
                }
            }
        }
    }
    post {
        always { echo "ProfileForge pipeline finished: ${currentBuild.currentResult}" }
    }
}
