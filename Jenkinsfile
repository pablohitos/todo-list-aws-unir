pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        S3_BUCKET = 'staging-todo-list-aws-pablo'
        STACK_NAME = 'staging-todo-list-aws'
        STAGE = 'default'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Clonando repositorio...'
                sh 'whoami && hostname'
                git credentialsId: 'github-token', url: 'https://github.com/pablohitos/todo-list-aws-unir', branch: 'develop'
            }
        }

        stage('Análisis Estático - Flake8') {
            steps {
                sh 'whoami && hostname'
                echo 'Ejecutando flake8...'
                sh 'python3 -m flake8 --format=pylint --exit-zero src > flake8-report.txt'
            }
        }

        stage('Análisis de Seguridad - Bandit') {
            steps {
                sh 'whoami && hostname'
                echo 'Ejecutando Bandit...'
                sh 'bandit -r src -f json -o bandit-report.json'
            }
        }

        stage('Despliegue Staging') {
            steps {
                sh 'whoami && hostname'
                echo 'Desplegando entorno Staging con SAM...'
                sh 'sam build'
                sh 'sam validate --region ${AWS_DEFAULT_REGION}'
                sh '''
                    sam deploy \
                        --stack-name ${STACK_NAME} \
                        --s3-bucket ${S3_BUCKET} \
                        --capabilities CAPABILITY_IAM \
                        --region ${AWS_DEFAULT_REGION} \
                        --parameter-overrides Stage=${STAGE} \
                        --no-fail-on-empty-changeset
                '''
            }
        }

        stage('Pruebas REST con Pytest') {
            steps {
                sh 'whoami && hostname'
                echo 'Ejecutando pruebas REST con Pytest...'
                sh '''
                    export PYTHONPATH=:$WORKSPACE/src
                    pytest test/ --junitxml=result.xml
                '''
            }
        }

        stage('Promoción a main') {
            steps {
                sh 'whoami && hostname'
                echo 'Promoviendo cambios a rama main...'
                withCredentials([usernamePassword(credentialsId: 'github-token-userpass', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    sh '''
                        git config --global user.email "jenkins@example.com"
                        git config --global user.name "Jenkins"
                        git checkout main
                        git merge develop
                        git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/pablohitos/todo-list-aws-unir main
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline de integración continua finalizado.'
            junit 'result.xml'

            // Publicar informe de flake8 usando pyLint parser
            recordIssues tools: [pyLint(pattern: 'flake8-report.txt')]

            // Guardar informe de bandit como artefacto
            archiveArtifacts artifacts: 'bandit-report.json', fingerprint: true
        }
    }
}
