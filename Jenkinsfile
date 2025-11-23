pipeline {
    agent any

    environment {
        FINNHUB_KEY = credentials('finnhub_api_key')
        SENDGRID_KEY = credentials('sendgrid_api_key')
        EMAIL_FROM = credentials('sendgrid_sender')
        EMAIL_TO = credentials('alert_email')
    }

    // Ejecutar automáticamente todos los días a las 8h (cron)
    triggers {
        cron('H 8 * * *')
    }

 stages {

        stage('Install dependencies') {
            steps {
                // Instalamos las librerías Python necesarias usando --break-system-packages
                sh 'python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt'
            }
        }

        stage('Ejecutar script') {
            steps {
                sh 'python3 scripts/check_insiders.py'
            }
        }
    }

    post {
        always {
            echo "Pipeline terminado."
        }
    }
}
