import tempfile

SECRET_KEY='...'
TESTING=True
db_fd, DATABASE = tempfile.mkstemp()
