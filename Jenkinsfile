pipeline {
    agent any

    environment {
        FINNHUB_API_KEY = credentials('FINNHUB_KEY')
    }

    stages {
        stage('Check Insider Trading') {
            steps {
                sh 'python3 scripts/check_insiders.py'
            }
        }
    }
}
