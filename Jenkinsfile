pipeline {
  agent any
  stages {
    stage('Run unit tests') {
      steps {
        sh '''source /home/ubuntu/miniconda3/bin/activate houseScraper
cd src
python -m unittest
source /home/ubuntu/miniconda3/bin/deactivate'''
      }
    }
  }
}