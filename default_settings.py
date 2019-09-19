import os

DATABASE='crossword_hints.db'
try:
    SECRET_KEY=os.environ['SECRET_KEY']
except KeyError:
    SECRET_KEY='HJuyjrRtyhy8hhjEDgYujNKUDL2356H'
TESTING=False
LDAP_PROVIDER_URL='ldap://localhost:389'
# Pagination settings
PER_PAGE=25
