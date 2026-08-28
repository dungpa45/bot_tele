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

                    env.REQUIREMENTS_HASH = currentHash

                    def savedHash = sh(
                        script: 'aws s3 cp s3://$S3_BUCKET/layers/requirements.sha256 /tmp/req.sha256 2>/dev/null && cat /tmp/req.sha256 || echo "NONE"',
                        returnStdout: true
                    ).trim()

                    def needsBuild = (savedHash == 'NONE') || (savedHash == '') || (currentHash != savedHash)

                    env.REQUIREMENTS_CHANGED = needsBuild.toString()

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
                                --compatible-runtimes python3.10 \
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

                    aws lambda wait function-updated \
                        --function-name "$FUNCTION_NAME"
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
                        script: 'aws sts get-caller-identity --query Account --output text',
                        returnStdout: true
                    ).trim()

                    env.LAYER_ARN = "arn:aws:lambda:${env.AWS_DEFAULT_REGION}:${accountId}:layer:${env.LAYER_NAME}:${env.LAYER_VERSION}"

                    sh '''
                        set -eux
                        aws lambda update-function-configuration \
                            --function-name "$FUNCTION_NAME" \
                            --layers "$LAYER_ARN"
                    '''
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