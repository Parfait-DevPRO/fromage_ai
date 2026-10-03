pipeline {
    agent any

    // Poll GitHub once per minute. For less frequent checks, use '*/5 * * * *'
    // or '*/15 * * * *' (the first field is minutes).
    triggers {
        pollSCM('*/1 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        // Replace with the Docker Hub namespace that owns the repository.
        DOCKERHUB_USER = 'your-dockerhub-user'
        IMAGE_NAME = 'fromazy-ai'
        IMAGE_TAG = "${BUILD_NUMBER}"

        // Create these credentials in Jenkins > Manage Jenkins > Credentials.
        DOCKERHUB_TOKEN_CREDENTIAL_ID = 'dockerhub-token'
        CD_WEBHOOK_URL = credentials('cd-webhook-url')
    }

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -eu
                    docker build --pull \
                      --tag "$DOCKERHUB_USER/$IMAGE_NAME:$IMAGE_TAG" \
                      --tag "$DOCKERHUB_USER/$IMAGE_NAME:latest" .
                '''
            }
        }

        stage('Publish to Registry') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([string(
                    credentialsId: env.DOCKERHUB_TOKEN_CREDENTIAL_ID,
                    variable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set -eu
                        set +x
                        printf '%s' "$DOCKERHUB_TOKEN" | docker login \
                          --username "$DOCKERHUB_USER" --password-stdin
                        docker push "$DOCKERHUB_USER/$IMAGE_NAME:$IMAGE_TAG"
                        docker push "$DOCKERHUB_USER/$IMAGE_NAME:latest"
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy via Webhook') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    set -eu
                    set +x
                    curl --fail --silent --show-error \
                      --max-time 30 --request POST "$CD_WEBHOOK_URL"
                '''
            }
        }
    }

    post {
        always {
            // Ignore missing images, such as when checkout or build failed.
            sh '''
                docker image rm -f \
                  "$DOCKERHUB_USER/$IMAGE_NAME:$IMAGE_TAG" \
                  "$DOCKERHUB_USER/$IMAGE_NAME:latest" >/dev/null 2>&1 || true
            '''
        }
    }
}
