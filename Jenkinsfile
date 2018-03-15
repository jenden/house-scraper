pipeline {
  agent any
  stages {
    stage('Run unit tests') {
      steps {
        sh '''source activate houseScraper
cd src
python -m unittest
source deactivate'''
      }
    }
  }
}