pipeline {
    agent any

    environment {
        FINNHUB_KEY = credentials('finnhub_api_key')
        SENDGRID_KEY = credentials('sendgrid_api_key')
        EMAIL_FROM = credentials('sendgrid_sender')
        EMAIL_TO = credentials('alert_email')
        VENV = 'venv'
    }

 stages {
        stage('Preparar entorno') {
            steps {
                sh '''
                python3 -m venv $VENV
                . $VENV/bin/activate
                pip install --break-system-packages --no-cache-dir -r requirements.txt
                '''
            }
        }

        stage('Ejecutar script') {
            steps {
                sh '''
                . $VENV/bin/activate
                python3 scripts/check_insiders.py
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline terminado."
        }
    }
}
