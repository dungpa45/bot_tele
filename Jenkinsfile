pipeline {

    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-southeast-1'

        FUNCTION_NAME = 'bot-linhtinh-tele'
        LAYER_NAME = 'tele'
        S3_BUCKET = 'dung-wp'

        AWS_CREDENTIALS = credentials('jenkins-role')
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
                    def currentHash = sh(
                        script: 'sha256sum requirements.txt | cut -d" " -f1',
                        returnStdout: true
                    ).trim()

                    def savedHash = sh(
                        script: 'aws s3 cp s3://$S3_BUCKET/layers/requirements.sha256 - 2>/dev/null || echo "NONE"',
                        returnStdout: true
                    ).trim()

                    def needsBuild
                    if (savedHash == 'NONE') {
                        // S3 chưa có hash → kiểm tra Lambda đã có layer chưa
                        def hasLayer = sh(
                            script: '''
                                aws lambda get-function-configuration \
                                    --function-name "$FUNCTION_NAME" \
                                    --query 'Layers' \
                                    --output text 2>/dev/null || echo "NONE"
                            ''',
                            returnStdout: true
                        ).trim()
                        def isFirstDeploy = (hasLayer == 'NONE' || hasLayer == 'None' || hasLayer == '')
                        needsBuild = isFirstDeploy
                        // Lambda đã có layer rồi → lưu hash hiện tại lên S3 để lần sau khỏi cần check lại
                        if (!isFirstDeploy) {
                            sh 'echo "$REQUIREMENTS_HASH" | aws s3 cp - s3://$S3_BUCKET/layers/requirements.sha256'
                        }
                    } else {
                        needsBuild = (currentHash != savedHash)
                    }

                    env.REQUIREMENTS_CHANGED = needsBuild.toString()
                    env.REQUIREMENTS_HASH = currentHash

                    echo "Current hash : ${currentHash}"
                    echo "Saved hash   : ${savedHash}"
                    echo "Will build layer: ${env.REQUIREMENTS_CHANGED}"
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
                    chmod +x ./build_layer.sh
                    ./build_layer.sh
                    du -sh packages.zip
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
                            aws s3 cp packages.zip s3://$S3_BUCKET/layers/packages.zip

                            aws lambda publish-layer-version \
                                --layer-name "$LAYER_NAME" \
                                --content S3Bucket=$S3_BUCKET,S3Key=layers/packages.zip \
                                --compatible-runtimes python3.12 \
                                --query 'Version' --output text
                        ''',
                        returnStdout: true
                    ).trim()

                    env.LAYER_VERSION = layerVersion
                    echo "Published Lambda Layer version: ${env.LAYER_VERSION}"

                    sh 'echo "$REQUIREMENTS_HASH" | aws s3 cp - s3://$S3_BUCKET/layers/requirements.sha256'
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

        stage('Test') {
            steps {
                sh '''
                    set -eux

                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements-dev.txt --quiet

                    TOKEN=x API_WEATHER=x API_AIRVISUAL=x API_NINJA=x \
                        PYTHONPATH=src .venv/bin/pytest tests/ -v --tb=short \
                        --junitxml=${WORKSPACE}/test-results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
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