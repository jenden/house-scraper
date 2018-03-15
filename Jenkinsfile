pipeline {
  agent any
  stages {
    stage('Run unit tests') {
      steps {
        sh '''/home/ubuntu/miniconda3/bin/activate houseScraper
cd src
python -m unittest
/home/ubuntu/miniconda3/bin/deactivate'''
      }
    }
  }
}