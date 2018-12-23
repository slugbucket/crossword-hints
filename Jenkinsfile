node('master') {
  stage("build") {
    deleteDir()
    sh """
    git clone -b develop https://github.com/slugbucket/crossword-hints.git
    virtualenv crossword-hints
    cd crossword-hints
    . ./bin/activate
     pip install -r pipfile
    """
  }
  stage("Unittests") {
    sh """
    cd crossword-hints
    APP_SETTINGS='test-settings.py' ./bin/python crossword-hints-tests.py
    """
  }
}
