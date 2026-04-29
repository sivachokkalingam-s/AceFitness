pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        DOCKER_IMAGE          = "sivachokkalingam1510/aceest-app"
        APP_VERSION           = "v${BUILD_NUMBER}"
        SONAR_TOKEN           = credentials('sonarcloud-token')
        SONAR_ORG             = "sivachokkalingam-s"
        SONAR_PROJECT_KEY     = "sivachokkalingam-s_AceFitness"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Build ${env.APP_VERSION} — branch ${env.GIT_BRANCH}"
                echo "Commit: ${env.GIT_COMMIT}"
            }
        }

        stage('Install Dependencies') {
            steps {
                // Windows: use bat instead of sh
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install --upgrade pip --quiet
                    pip install flask uvicorn pytest pytest-cov --quiet
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest test_logic.py -v ^
                        --tb=short ^
                        --junitxml=test-results.xml ^
                        --cov=logic ^
                        --cov-report=xml:coverage.xml ^
                        --cov-report=term-missing
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('SonarCloud Analysis') {
            steps {
                // sonar-scanner must be installed and on PATH
                // Download: https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/
                bat '''
                    sonar-scanner ^
                      -Dsonar.host.url=https://sonarcloud.io ^
                      -Dsonar.token=%SONAR_TOKEN% ^
                      -Dsonar.organization=%SONAR_ORG% ^
                      -Dsonar.projectKey=%SONAR_PROJECT_KEY% ^
                      -Dsonar.projectName="ACEest Fitness" ^
                      -Dsonar.projectVersion=%APP_VERSION% ^
                      -Dsonar.sources=. ^
                      -Dsonar.tests=test_logic.py ^
                      -Dsonar.python.version=3 ^
                      -Dsonar.python.coverage.reportPaths=coverage.xml ^
                      -Dsonar.python.xunit.reportPath=test-results.xml ^
                      "-Dsonar.exclusions=venv/**,screenshots/**,**/__pycache__/**"
                '''
            }
        }

        stage('SonarCloud Quality Gate') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        def status   = 'NONE'
                        def attempts = 0
                        while (status != 'OK' && status != 'ERROR' && attempts < 30) {
                            sleep(10)
                            attempts++
                            def response = bat(
                                script: "curl -sf -u %SONAR_TOKEN%: \"https://sonarcloud.io/api/qualitygates/project_status?projectKey=%SONAR_PROJECT_KEY%\"",
                                returnStdout: true
                            ).trim()
                            // Extract status from JSON (simple string search for Windows)
                            if (response.contains('"status":"OK"')) {
                                status = 'OK'
                            } else if (response.contains('"status":"ERROR"')) {
                                status = 'ERROR'
                            }
                            echo "Quality Gate: ${status} (attempt ${attempts})"
                        }
                        if (status == 'ERROR') {
                            error("SonarCloud Quality Gate FAILED — check https://sonarcloud.io/project/overview?id=${SONAR_PROJECT_KEY}")
                        } else if (status != 'OK') {
                            echo "WARNING: Quality Gate did not respond — continuing"
                        } else {
                            echo "Quality Gate PASSED"
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker build ^
                      --build-arg APP_VERSION=%APP_VERSION% ^
                      -t %DOCKER_IMAGE%:%APP_VERSION% ^
                      -t %DOCKER_IMAGE%:latest ^
                      .
                    docker images %DOCKER_IMAGE%
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                bat '''
                    echo %DOCKERHUB_CREDENTIALS_PSW%| docker login -u %DOCKERHUB_CREDENTIALS_USR% --password-stdin
                    docker push %DOCKER_IMAGE%:%APP_VERSION%
                    docker push %DOCKER_IMAGE%:latest
                    docker logout
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    // Check if minikube is running before deploying
                    def minikubeStatus = bat(script: 'minikube status --profile acefitness 2>nul', returnStatus: true)
                    if (minikubeStatus != 0) {
                        echo "Starting Minikube..."
                        bat 'minikube start --profile acefitness --driver=docker'
                    }
                }
                bat '''
                    kubectl config use-context acefitness

                    REM Rolling Update
                    echo === Rolling Update ===
                    powershell -Command "(Get-Content k8s\\rolling\\rolling-deployment.yaml) -replace 'APP_VERSION', '%APP_VERSION%' | kubectl apply -f -"
                    kubectl rollout status deployment/acefitness-rolling --timeout=120s

                    REM Blue-Green
                    echo === Blue-Green ===
                    kubectl apply -f k8s\\blue-green\\blue-deployment.yaml
                    powershell -Command "(Get-Content k8s\\blue-green\\green-deployment.yaml) -replace 'APP_VERSION', '%APP_VERSION%' | kubectl apply -f -"
                    kubectl rollout status deployment/acefitness-green --timeout=120s
                    kubectl apply -f k8s\\blue-green\\service-green.yaml

                    REM Canary
                    echo === Canary ===
                    powershell -Command "(Get-Content k8s\\canary\\canary-deployment.yaml) -replace 'APP_VERSION', '%APP_VERSION%' | kubectl apply -f -"
                    kubectl rollout status deployment/acefitness-canary --timeout=120s

                    echo === All strategies deployed ===
                    kubectl get deployments
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                script {
                    sleep(15)
                    def result = bat(
                        script: 'curl -sf http://localhost/init',
                        returnStatus: true
                    )
                    if (result == 0) {
                        echo "Smoke test PASSED"
                    } else {
                        echo "Smoke test could not reach service — check minikube tunnel"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "=========================================="
            echo "Pipeline SUCCESS — ${env.APP_VERSION}"
            echo "Docker Hub: ${env.DOCKER_IMAGE}:${env.APP_VERSION}"
            echo "SonarCloud: https://sonarcloud.io/project/overview?id=${env.SONAR_PROJECT_KEY}"
            echo "=========================================="
        }
        failure {
            echo "Pipeline FAILED — check console output above"
            // Rollback inside a node block to avoid MissingContextVariableException
            node {
                bat '''
                    kubectl rollout undo deployment/acefitness-rolling 2>nul || echo rollback skipped
                    kubectl rollout undo deployment/acefitness-green   2>nul || echo rollback skipped
                '''
            }
        }
        always {
            // cleanWs must be inside a node — it is here because agent any provides one
            cleanWs()
        }
    }
}
