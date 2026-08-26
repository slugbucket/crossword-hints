# -*- coding: utf-8 -*-
"""
Crossword hints initialisation
"""

import logging
import os
import sqlite3
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    jsonify,
    Response,
    send_file,
    url_for,
)
from peewee import SqliteDatabase, DoesNotExist, OperationalError
from werkzeug.exceptions import NotFound, InternalServerError

# from crossword_hints.controllers import (
#     setter_types,
#     crossword_setters,
#     solution_types,
#     crossword_solutions,
#     crossword_hints,
#     cue_words,
# )
# from jur_oauth2_login.controllers import login

# Based on https://github.com/salimane/flask-mvc/blob/master/project/__init__.py
__version__ = "1.0.25"
__all__ = ["models", "views", "controllers"]

application = Flask(__name__, template_folder="views/templates")

try:
    os.environ["APP_SETTINGS"]
except KeyError:
    os.environ["APP_SETTINGS"] = os.path.join(
        application.root_path, "default_settings.py"
    )
    print(f"Loading default settings from {os.environ['APP_SETTINGS']}")

# Create an application handle that AWS EB can understand
application.config.from_envvar("APP_SETTINGS")

database = SqliteDatabase(
    application.config["DATABASE"], pragmas=(("foreign_keys", "on"),)
)
database.row_factory = sqlite3.Row

from crossword_hints.views.crossword_hints import url_for_other_page, highlight_text

logger = logging.getLogger("flask")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.ERROR)

application.jinja_env.globals["url_for_other_page"] = url_for_other_page
application.jinja_env.filters["highlight_text"] = highlight_text

# Import controllers after the application exists so their route decorators run.
from crossword_hints.controllers import (
    crossword_hints,
    crossword_setters,
    crossword_solutions,
    cue_words,
    setter_types,
    solution_types,
)


def custom_error_handler(e):
    """     E  X  C  E  P  T  I  O  N    H  A  N  D  L  I  N  G    """
    return jsonify({"error": str(e)})  # Return a JSON response with the error message


@application.errorhandler(DoesNotExist)
def handle_database_error(error):
    """
    Handle database error
    """
    return (render_template("errors/409.html", errmsg=error), 409)


@application.errorhandler(409)
def handle_409_error(error):
    """
    Handle 409 error
    """
    return (render_template("errors/409.html", errmsg=error), 409)


@application.errorhandler(OperationalError)
def handle_operational_error(error):
    """
    Handle operational error
    """
    return (render_template("errors/409.html", errmsg=error), 409)


@application.errorhandler(NotFound)
def handle_page_not_found_error(error):
    """
    Handle page not found error
    """
    return render_template("errors/404.html", errmsg=error), 404


@application.errorhandler(InternalServerError)
def handle_server_error(error):
    """
    Handle 500 server error
    """
    return render_template("errors/500.html", errmsg=error), 500
