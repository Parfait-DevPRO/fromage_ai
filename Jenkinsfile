pipeline {
    agent any

    triggers {
        pollSCM('*/1 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        // Mettez ici votre nom d'utilisateur Docker Hub officiel
        DOCKERHUB_USER = 'parfaitdevpro'
        IMAGE_NAME = 'fromazy-ai'
        IMAGE_TAG = "${BUILD_NUMBER}"

        DOCKERHUB_TOKEN_CREDENTIAL_ID = 'dockerhub-token'
    }

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
<<<<<<< HEAD
                bat """
                    docker build --pull ^
                      --tag %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% ^
                      --tag %DOCKERHUB_USER%/%IMAGE_NAME%:latest .
                """
=======
                powershell '''
                    $ErrorActionPreference = 'Stop'
                    docker build --pull `
                      --tag "$env:DOCKERHUB_USER/$env:IMAGE_NAME:$env:IMAGE_TAG" `
                      --tag "$env:DOCKERHUB_USER/$env:IMAGE_NAME:latest" .
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                '''
>>>>>>> 6dc7c09 (Modification Jenkinsfile)
            }
        }

        stage('Publish to Registry') {
            steps {
                withCredentials([string(
                    credentialsId: env.DOCKERHUB_TOKEN_CREDENTIAL_ID,
                    variable: 'DOCKERHUB_TOKEN'
                )]) {
<<<<<<< HEAD
                    bat """
                        @echo off
                        echo %DOCKERHUB_TOKEN% | docker login --username %DOCKERHUB_USER% --password-stdin
                        docker push %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG%
                        docker push %DOCKERHUB_USER%/%IMAGE_NAME%:latest
                        docker logout
                    """
=======
                    powershell '''
                        $ErrorActionPreference = 'Stop'
                        $env:DOCKERHUB_TOKEN | docker login `
                          --username $env:DOCKERHUB_USER --password-stdin
                        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                        docker push "$env:DOCKERHUB_USER/$env:IMAGE_NAME:$env:IMAGE_TAG"
                        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                        docker push "$env:DOCKERHUB_USER/$env:IMAGE_NAME:latest"
                        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                        docker logout
                        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                    '''
>>>>>>> 6dc7c09 (Modification Jenkinsfile)
                }
            }
        }

        stage('Deploy via Webhook') {
            steps {
<<<<<<< HEAD
                powershell """
                    Invoke-RestMethod -Uri "${env.CD_WEBHOOK_URL}" -Method Post -TimeoutSec 30
                """
=======
                withCredentials([string(credentialsId: 'cd-webhook-url', variable: 'CD_WEBHOOK_URL')]) {
                    powershell '''
                        $ErrorActionPreference = 'Stop'
                        curl.exe --fail --silent --show-error `
                          --max-time 30 --request POST $env:CD_WEBHOOK_URL
                        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                    '''
                }
>>>>>>> 6dc7c09 (Modification Jenkinsfile)
            }
        }
    }

    post {
        always {
<<<<<<< HEAD
            // Cette enveloppe 'node' garantit à 100% la présence du contexte hudson.FilePath requis sous Windows
            node {
                bat """
                    docker image rm -f %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% 2>nul || exit 0
                    docker image rm -f %DOCKERHUB_USER%/%IMAGE_NAME%:latest 2>nul || exit 0
                """
            }
=======
            // Pipeline-level agent any keeps a workspace available for cleanup.
            powershell '''
                $ErrorActionPreference = 'Continue'
                docker image rm -f `
                  "$env:DOCKERHUB_USER/$env:IMAGE_NAME:$env:IMAGE_TAG" `
                  "$env:DOCKERHUB_USER/$env:IMAGE_NAME:latest" 2>$null
                exit 0
            '''
>>>>>>> 6dc7c09 (Modification Jenkinsfile)
        }
    }
}
