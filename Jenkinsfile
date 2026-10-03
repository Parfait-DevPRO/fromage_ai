pipeline {
    agent any

    triggers {
        pollSCM('*/1 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        // Mettez ici votre nom d'utilisateur Docker Hub officiel
        DOCKERHUB_USER = 'parfaitdevpro'
        IMAGE_NAME = 'fromazy-ai'
        IMAGE_TAG = "${BUILD_NUMBER}"

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
                bat """
                    docker build --pull ^
                      --tag %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% ^
                      --tag %DOCKERHUB_USER%/%IMAGE_NAME%:latest .
                """
            }
        }

        stage('Publish to Registry') {
            steps {
                withCredentials([string(
                    credentialsId: env.DOCKERHUB_TOKEN_CREDENTIAL_ID,
                    variable: 'DOCKERHUB_TOKEN'
                )]) {
                    bat """
                        @echo off
                        echo %DOCKERHUB_TOKEN% | docker login --username %DOCKERHUB_USER% --password-stdin
                        docker push %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG%
                        docker push %DOCKERHUB_USER%/%IMAGE_NAME%:latest
                        docker logout
                    """
                }
            }
        }

        stage('Deploy via Webhook') {
            steps {
                powershell """
                    Invoke-RestMethod -Uri "${env.CD_WEBHOOK_URL}" -Method Post -TimeoutSec 30
                """
            }
        }
    }

    post {
        always {
            // Cette enveloppe 'node' garantit à 100% la présence du contexte hudson.FilePath requis sous Windows
            node {
                bat """
                    docker image rm -f %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% 2>nul || exit 0
                    docker image rm -f %DOCKERHUB_USER%/%IMAGE_NAME%:latest 2>nul || exit 0
                """
            }
        }
    }
}
