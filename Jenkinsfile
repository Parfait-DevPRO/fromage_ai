pipeline {
    agent any

    // Vérification du dépôt GitHub toutes les minutes via Poll SCM
    triggers {
        pollSCM('*/1 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        // Remplacer par votre nom d'utilisateur Docker Hub officiel
        DOCKERHUB_USER = 'your-dockerhub-user'
        IMAGE_NAME = 'fromazy-ai'
        IMAGE_TAG = "${BUILD_NUMBER}"

        // ID de vos identifiants dans Jenkins (Jenkins > Credentials)
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
                // Utilisation de 'bat' sous Windows avec la syntaxe de variables de batch (%VAR%)
                bat """
                    docker build --pull ^
                      --tag %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% ^
                      --tag %DOCKERHUB_USER%/%IMAGE_NAME%:latest .
                """
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
                    // Connexion sécurisée et push natifs Windows
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
            when {
                branch 'main'
            }
            steps {
                // Utilisation de curl natif Windows ou de l'utilitaire PowerShell via Jenkins
                powershell """
                    Invoke-RestMethod -Uri "${env.CD_WEBHOOK_URL}" -Method Post -TimeoutSec 30
                """
            }
        }
    }

    post {
        always {
            // Nettoyage sécurisé du stockage local Windows
            bat """
                docker image rm -f %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% 2>nul || exit 0
                docker image rm -f %DOCKERHUB_USER%/%IMAGE_NAME%:latest 2>nul || exit 0
            """
        }
    }
}
