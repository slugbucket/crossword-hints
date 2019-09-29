import tempfile

SECRET_KEY='wwwfnegegghtj6jl565msberthfiwhfi'
TESTING=True
db_fd, DATABASE = tempfile.mkstemp()
LOGIN_DISABLED=True
PER_PAGE              = 25
NUM_SOLUTION_ROWS     = 760
NUM_SOLUTION_TYPES    = 18
NUM_CROSSWORD_SETTERS = 32
NUM_SETTER_TYPES      = 5