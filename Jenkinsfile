pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        S3_BUCKET = 'production-todo-list-aws-pablo'
        STACK_NAME = 'production-todo-list-aws'
        STAGE = 'production'
        BASE_URL = 'https://wjjvpkiebg.execute-api.us-east-1.amazonaws.com/Prod'
    }

    stages {
        stage('Checkout') {
            steps {
                sh 'whoami && hostname'
                echo 'Clonando rama main...'
                git credentialsId: 'github-token', url: 'https://github.com/pablohitos/todo-list-aws-unir', branch: 'main'
            }
        }

        stage('Despliegue Producción') {
            steps {
                sh 'whoami && hostname'
                echo 'Desplegando entorno Producción con SAM...'
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

        stage('Pruebas de Lectura (Pytest)') {
            steps {
                sh 'whoami && hostname'
                echo 'Ejecutando pruebas de solo lectura con Pytest...'
                sh '''
                    export PYTHONPATH=:$WORKSPACE/src
                    export BASE_URL=${BASE_URL}
                    pytest test/integration/todoApiTest.py --junitxml=result.xml
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline de entrega continua (CD) finalizado.'
            junit 'result.xml'
        }
    }
}
