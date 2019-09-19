import tempfile

SECRET_KEY='wwwfnegegghtj6jl565msberthfiwhfi'
TESTING=True
db_fd, DATABASE = tempfile.mkstemp()
LOGIN_DISABLED=True
PER_PAGE=25