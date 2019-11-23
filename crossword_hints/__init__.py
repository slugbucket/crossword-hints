# -*- coding: utf-8 -*-
from flask import Flask, request, flash, redirect, render_template, g, jsonify, Response, send_file, url_for
import os

# Based on https://github.com/salimane/flask-mvc/blob/master/project/__init__.py
__version__ = '1.0.25'
__all__ = ["models", "views", "controllers"]

application = Flask(__name__, template_folder="views/templates") or create_app('runserver.py', template_folder="views")

try:
    os.environ['APP_SETTINGS']
except KeyError:
    os.environ['APP_SETTINGS'] = os.path.join(application.root_path, 'default_settings.py')

# Create an application handle that AWS EB can understand
application.config.from_envvar('APP_SETTINGS')

# Print all queries to stderr.
#import logging
#logger = logging.getLogger('peewee')
#logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)

from crossword_hints.views.crossword_hints import *
from crossword_hints.controllers import setter_types, crossword_setters, solution_types, crossword_solutions, crossword_hints, cue_words

application.jinja_env.globals['url_for_other_page'] = url_for_other_page

"""                                                        """
"""  E  X  C  E  P  T  I  O  N    H  A  N  D  L  I  N  G   """
"""                                                        """
@application.errorhandler(DoesNotExist)
def handle_database_error(error):
    return(render_template('errors/409.html', errmsg=error), 409)
@application.errorhandler(409)
def handle_409_error(error):
    return(render_template('errors/409.html', errmsg=error), 409)
@application.errorhandler(OperationalError)
def handle_operational_error(error):
    return(render_template('errors/409.html', errmsg=error), 409)
@application.errorhandler(404)
def handle_opertional_error(error):
    return(render_template('errors/404.html', errmsg=error))
@application.errorhandler(500)
def handle_opertional_error(error):
    return(render_template('errors/500.html', errmsg=error))
