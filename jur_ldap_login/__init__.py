# -*- coding: utf-8 -*-

import ldap
from flask_login import LoginManager, UserMixin, current_user, \
                                login_required, login_user, logout_user
from crossword_hints import application

def get_ldap_connection():
    conn = ldap.initialize(application.config['LDAP_PROVIDER_URL'])
    return conn
