#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crossword hints start script
"""
import os

# Load the local application and login packages
from crossword_hints import application
# from jur_oauth2_login import *

# To run the application as standalone,
# export FLASK_APP=runserver.py
# flask run
# or, to support SSL, use
# flask run --cert=adhoc
# or, with uwsgi,
# uwsgi --ini crossword_hints.ini
#

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port, ssl_context="adhoc")
    # application.run(host="0.0.0.0",ssl_context="adhoc")
