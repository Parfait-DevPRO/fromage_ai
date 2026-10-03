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
        powershell '''
            $ErrorActionPreference = 'Stop'

            $image = "$($env:DOCKERHUB_USER)/$($env:IMAGE_NAME):$($env:IMAGE_TAG)"
            $latest = "$($env:DOCKERHUB_USER)/$($env:IMAGE_NAME):latest"

            Write-Host "Building image: $image"
            Write-Host "Building image: $latest"

            docker build --pull `
              --tag $image `
              --tag $latest .

            if ($LASTEXITCODE -ne 0) {
                exit $LASTEXITCODE
            }
        '''
    }
}

    stage('Publish to Registry') {
    steps {
        withCredentials([string(
            credentialsId: env.DOCKERHUB_TOKEN_CREDENTIAL_ID,
            variable: 'DOCKERHUB_TOKEN'
        )]) {
            powershell '''
                $ErrorActionPreference = 'Stop'

                $image = "$($env:DOCKERHUB_USER)/$($env:IMAGE_NAME):$($env:IMAGE_TAG)"
                $latest = "$($env:DOCKERHUB_USER)/$($env:IMAGE_NAME):latest"

                Write-Host "Pushing image: $image"
                Write-Host "Pushing image: $latest"

                $env:DOCKERHUB_TOKEN | docker login `
                    --username $env:DOCKERHUB_USER `
                    --password-stdin

                if ($LASTEXITCODE -ne 0) {
                    exit $LASTEXITCODE
                }

                docker push $image

                if ($LASTEXITCODE -ne 0) {
                    exit $LASTEXITCODE
                }

                docker push $latest

                if ($LASTEXITCODE -ne 0) {
                    exit $LASTEXITCODE
                }

                docker logout
            '''
        }
    }
}

        stage('Deploy via Webhook') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'cd-webhook-url',
                        variable: 'CD_WEBHOOK_URL'
                    )
                ]) {
                    powershell '''
                        $ErrorActionPreference = 'Stop'

                        curl.exe --fail --silent --show-error `
                          --max-time 30 `
                          --request POST `
                          $env:CD_WEBHOOK_URL

                        if ($LASTEXITCODE -ne 0) {
                            exit $LASTEXITCODE
                        }
                    '''
                }
            }
        }
    }

    post {
        always {
            powershell '''
                $ErrorActionPreference = 'Continue'

                docker image rm -f `
                  "$env:DOCKERHUB_USER/$env:IMAGE_NAME:$env:IMAGE_TAG" `
                  "$env:DOCKERHUB_USER/$env:IMAGE_NAME:latest" 2>$null

                exit 0
            '''
        }
    }
}
