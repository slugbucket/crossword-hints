#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

# Load the local application and login packages
from crossword_hints import application
#from jur_ldap_login import *

# To run the application as standalone,
# export FLASK_APP=crossword_hints.py
# flask run
# or, with uwsgi,
# uwsgi --ini crossword_hints.ini
#

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
