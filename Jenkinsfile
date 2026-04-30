pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        DOCKER_IMAGE = "sivachokkalingam1510/aceest-app"
        SONAR_HOST_URL = "https://sonarcloud.io"
        SONAR_PROJECT_KEY = "sivachokkalingam-s_AceFitness"
        SONAR_ORGANIZATION = "sivachokkalingam-s"
        APP_VERSION = "v${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/sivachokkalingam-s/AceFitness.git'
                echo "Checked out commit: ${GIT_COMMIT}"
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_logic.py -v --tb=short --junitxml=test-results.xml --cov=logic --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        ${SONARQUBE_SCANNER_HOME}/bin/sonar-scanner \
                          -Dsonar.projectKey=AceFit \
                          -Dsonar.projectName="ACEFit Fitness" \
                          -Dsonar.projectVersion=${APP_VERSION} \
                          -Dsonar.sources=. \
                          -Dsonar.language=py \
                          -Dsonar.python.version=3.10 \
                          -Dsonar.sourceEncoding=UTF-8 \
                          -Dsonar.coverage.exclusions=**/templates/**,**/*.md
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      --build-arg APP_VERSION=${APP_VERSION} \
                      -t ${DOCKER_IMAGE}:${APP_VERSION} \
                      -t ${DOCKER_IMAGE}:latest \
                      .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh '''
                    echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
                    docker push ${DOCKER_IMAGE}:${APP_VERSION}
                    docker push ${DOCKER_IMAGE}:latest
                    docker logout
                '''
            }
        }

        stage('Deploy - Rolling Update') {
            when { branch 'main' }
            steps {
                sh '''
                    kubectl set image deployment/acefitness-rolling \
                      acefitness=${DOCKER_IMAGE}:${APP_VERSION} \
                      --record || true
                    kubectl rollout status deployment/acefitness-rolling --timeout=120s || true
                '''
            }
        }

        stage('Deploy - Blue/Green') {
            when { branch 'main' }
            steps {
                sh '''
                    # Deploy green version
                    kubectl apply -f k8s/k8s-green-deployment.yaml || true
                    kubectl rollout status deployment/acefitness-green --timeout=120s || true
                    # Switch traffic to green
                    kubectl apply -f k8s/k8s-service-green.yaml || true
                    echo "Traffic switched to GREEN (${APP_VERSION})"
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    sleep 10
                    kubectl run smoke-test --image=curlimages/curl --restart=Never --rm -i \
                      -- curl -sf http://acefitness-service/init && echo "Smoke test PASSED" || true
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Version ${APP_VERSION} deployed."
            cleanWs()
        }
        failure {
            echo "Pipeline FAILED. Initiating rollback..."
            sh '''
                kubectl rollout undo deployment/acefitness-rolling || true
                kubectl rollout undo deployment/acefitness-green || true
            '''
            cleanWs()
        }
        always {
            sh 'docker system prune -f'
        }
    }
}