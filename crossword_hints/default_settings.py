# -*- coding: utf-8 -*-
import os

DATABASE = "crossword_hints.db"
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
TESTING = False
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
# Pagination settings
PER_PAGE = 25
