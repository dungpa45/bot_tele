pipeline {

    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-southeast-1'

        FUNCTION_NAME = 'my-lambda-function'
        LAYER_NAME = 'my-lambda-layer'

        AWS_CREDENTIALS = credentials('aws-lambda')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(false)
    }

    stages {

        stage('Detect Changes') {
            steps {
                script {
                    def requirementsChanged = currentBuild.changeSets.any { changeSet ->
                        changeSet.items.any { item ->
                            item.affectedFiles.any { file ->
                                file.path == 'requirements.txt'
                            }
                        }
                    }

                    env.REQUIREMENTS_CHANGED = requirementsChanged.toString()

                    echo "requirements.txt changed: ${env.REQUIREMENTS_CHANGED}"
                }
            }
        }

        stage('Build Lambda Layer') {
            when {
                expression {
                    env.REQUIREMENTS_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    set -eux

                    chmod +x ./build-layer.sh

                    ./build-layer.sh

                    test -f packages.zip
                '''
            }
        }

        stage('Publish Lambda Layer') {
            when {
                expression {
                    env.REQUIREMENTS_CHANGED == 'true'
                }
            }

            steps {
                script {
                    def layerVersion = sh(
                        script: '''
                            aws lambda publish-layer-version \
                                --layer-name "$LAYER_NAME" \
                                --zip-file fileb://packages.zip \
                                --compatible-runtimes python3.12 \
                                --query 'Version' \
                                --output text
                        ''',
                        returnStdout: true
                    ).trim()

                    env.LAYER_VERSION = layerVersion

                    echo "Published Lambda Layer version: ${env.LAYER_VERSION}"
                }
            }
        }

        stage('Package Lambda') {
            steps {
                sh '''
                    set -eux

                    rm -f lambda-function.zip

                    cd src

                    zip -r -9 ../lambda-function.zip .
                '''
            }
        }

        stage('Deploy Lambda Code') {
            steps {
                sh '''
                    set -eux

                    aws lambda update-function-code \
                        --function-name "$FUNCTION_NAME" \
                        --zip-file fileb://lambda-function.zip
                '''
            }
        }

        stage('Update Lambda Layer') {
            when {
                expression {
                    env.REQUIREMENTS_CHANGED == 'true'
                }
            }

            steps {
                script {
                    def accountId = sh(
                        script: '''
                            aws sts get-caller-identity \
                                --query Account \
                                --output text
                        ''',
                        returnStdout: true
                    ).trim()

                    sh """
                        set -eux

                        aws lambda update-function-configuration \
                            --function-name "$FUNCTION_NAME" \
                            --layers \
                            arn:aws:lambda:${AWS_DEFAULT_REGION}:${accountId}:layer:${LAYER_NAME}:${LAYER_VERSION}
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }

        success {
            echo 'Lambda deployment completed successfully.'
        }

        failure {
            echo 'Lambda deployment failed.'
        }
    }
}