from flask import Flask, request, flash, redirect, render_template, g, jsonify, Response, send_file
from werkzeug import Headers
from jinja2 import Environment, PackageLoader, select_autoescape
import sqlite3
import json
import os
import io
import re
import tempfile
import zipfile
import socket
from peewee import *
import datetime
from datetime import date, timedelta, datetime

# To run the application as standalone,
# export FLASK_APP=xword-hints.py
# flask run
# or, with uwsgi,
# uwsgi --ini crossword_hints.ini
#
app = Flask(__name__)
try:
    os.environ['APP_SETTINGS']
except KeyError:
    os.environ['APP_SETTINGS'] = os.path.join(app.root_path, 'default_settings.py')

app.config.from_envvar('APP_SETTINGS')
database = SqliteDatabase(app.config['DATABASE'], pragmas=(("foreign_keys", "on"),))
database.row_factory = sqlite3.Row

# This hook ensures that a connection is opened to handle any queries
# generated by the request.
#@app.before_request
#def _db_connect():
#    #database.get_conn()

# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()


"""
Initialise the database - only to be used for testing and database restore
To bootstrap a database, either empty or with new schema:
$ python
>>> import crossword_hints
>>> from peewee import *
>>> with .app.app_context():
...     crossword_hints.init_db()
Params:
  None
Returns:
  None
"""
def init_db():
    for tbl in ['setter_types', 'crossword_setters', 'solution_types', 'crossword_solutions']:
        database.execute_sql("drop table " + tbl)
    database.create_tables(['setter_types', 'crossword_setters', 'solution_types', 'crossword_solutions'])


"""
Index listing of known solutions
Params:
  None
Returns:
  jinja2 template render of list of active requests
"""
@app.route("/xword-hints/", methods=["GET"], defaults={'path': ''})
@app.route('/', defaults={'path': ''})
def crossowrd_hints_index(path):
    rs = crossword_solutions.select()
    return(render_template('views/crossword-hints/index.html', r=request))


"""
Index listing of known setters
"""
@app.route("/crossword-setters/", methods=["GET"])
def crossword_setters_index():
    rs = crossword_setters.select(crossword_setters.rowid, crossword_setters.name, setter_types.name.alias('setter_type_name')).join(setter_types).where(crossword_setters.setter_type_id == setter_types.rowid)
    print("DEBUG: setter type is %s." % rs)
    for row in rs.dicts():
        print("DEBUG: crossword_setters_index: Found %s." % row['setter_type_name'])
    return render_template('views/crossword-setters/index.html', setters=rs.dicts(), r=request)

@app.route("/crossword-setters/<int:id>", methods=["GET"])
def crossword_setters_show(id):
    # Getting the setter id, name and setter_type name should be a simple inner
    # join across the tables but Peewee makes a complete mess of it so it is
    # easier to do raw SQL instead.
    #rs = crossword_setters.get(crossword_setters.rowid, crossword_setters.name, setter_types.name.alias('setter_type_name')).join(setter_types, JOIN.INNER).where((crossword_setters.setter_type_id == setter_types.rowid) & (crossword_setters.rowid == id))
    rs = crossword_setters.raw('SELECT t1.name, t2.name AS setter_type_name FROM crossword_setters t1 INNER JOIN setter_types t2 ON t1.setter_type_id = t2.rowid  AND t1.rowid = ?', id).tuples()
    print("DEBUG: crossword_setters_show: Retrieved raw SQL object: %s." % rs)
    for sname, stname in rs:
        stype = {"rowid": id, "name": sname, "setter_type_name": stname}
        print("DEBUG: setter is %s of type %s." % (sname, stname))
    return render_template('views/crossword-setters/show.html', stype=stype,  r=request)

"""
Add a new crossowrd setter
"""
@app.route("/crossword-setters/new", methods=["GET"])
def crossword_setters_new():
    setter={'name': "New setter", 'setter_type_id': 1}
    return render_template('views/crossword-setters/new.html', setter=setter, s_types=get_setter_types(), r=request)

"""
Edit an existing setter
"""
@app.route("/crossword-setters/<int:id>/edit", methods=["GET"])
def crossword_setters_edit(id):
    rs = crossword_setters.get(crossword_setters.rowid == id)
    return render_template('views/crossword-setters/edit.html', setter=rs, s_types=get_setter_types(), r=request)

"""              """
""" Setter types """
"""              """
@app.route("/setter-types/", methods=["GET"])
def setter_types_index():
    rs = setter_types.select()
    return render_template('views/setter-types/index.html', stypes=rs.dicts(), r=request)

@app.route("/setter-types/<int:id>", methods=["GET"])
def setter_types_show(id):
    rs = setter_types.get(setter_types.rowid == id)
    return render_template('views/setter-types/show.html', stype=rs,  r=request)

@app.route("/setter-types/new", methods=["GET", "POST"])
def setter_types_new():
    stype={'name': "New setter type", 'description': 'Brief description of this type of setter'}
    return render_template('views/setter-types/new.html', stype=stype,  r=request)

@app.route("/setter-types/<int:id>/edit", methods=["GET", "POST"])
def setter_types_edit(id):
    rs = setter_types.get(setter_types.rowid == id)
    return render_template('views/setter-types/edit.html', stype=rs, r=request)

"""               """
""" Soluion types """
"""               """
@app.route("/solution-types/", methods=["GET"])
def solution_types_index():
    rs = solution_types.select()
    return render_template('views/solution-types/index.html', stypes=rs.dicts(), r=request)

@app.route("/solution-types/<int:id>", methods=["GET"])
def solution_types_show(id):
    rs = solution_types.get(solution_types.rowid == id)
    return render_template('views/solution-types/show.html', stype=rs,  r=request)

@app.route("/solution-types/new", methods=["GET", "POST"])
def solution_types_new():
    stype={'name': "New solution type", 'description': 'Brief description of this type of solution'}
    return render_template('views/solution-types/new.html', stype=stype,  r=request)

@app.route("/solution-types/<int:id>/edit", methods=["GET", "POST"])
def solution_types_edit(id):
    rs = solution_types.get(solution_types.rowid == id)
    print("DEBUG: solution_types_edit: Editing solution type, %s." % rs.name)
    return render_template('views/solution-types/edit.html', stype=rs, r=request)

@app.route("/solution-types/<int:id>/delete", methods=["GET", "POST"])
def solution_types_delete(id):
    pass

"""                                                        """
"""  E  X  C  E  P  T  I  O  N    H  A  N  D  L  I  N  G   """
"""                                                        """
@app.errorhandler(DoesNotExist)
def handle_database_error(error):
    return(render_template('errors/409.html', errmsg=error))
@app.errorhandler(OperationalError)
def handle_opertional_error(error):
    return(render_template('errors/409.html', errmsg=error))

"""                                                        """
"""  I  N  T  E  R  N  A  L    F  U  N  C  T  I  O  N  S   """
"""                                                        """
"""
Construct an array containing the setter_type rowid and name
suitable for use in a SELECT from element
"""
def get_setter_types():
    rs=setter_types.select(setter_types.rowid, setter_types.name)
    s_types = []
    for row in rs.dicts():
        s_types.append([row['rowid'], row['name']])
    return(s_types)


"""                                                        """
"""  D  A  T  A  B  A  S  E     M  O  D  E  L  L  I  N  G  """
"""                                                        """
"""                                                        """
"""     A base model that will use our Sqlite database.    """
"""     Appears to be incompatible with Flask TestCase     """
class BaseModel(Model):
    with app.app_context():
        class Meta:
            database = database

class activity_logs(BaseModel):
    rowid          = AutoField()
    action         = CharField(max_length=32)
    item           = CharField(max_length=32)
    item_id        = IntegerField()
    activity       = TextField()
    updated_by     = CharField(max_length=32)
    updated_at     = DateTimeField(default=datetime.now())

class setter_types(BaseModel):
    rowid          = AutoField()
    name           = CharField(null=False, max_length=16, unique=True)
    description    = TextField()
    created_at     = DateTimeField(default=datetime.now())
    updated_at     = DateTimeField(default=datetime.now())

class crossword_setters(BaseModel):
    rowid          = AutoField()
    name           = CharField(null=False, unique=True, max_length=32)
    setter_type    = ForeignKeyField(setter_types)
    created_at     = DateTimeField(default=datetime.now())
    updated_at     = DateTimeField(default=datetime.now())


class solution_types(BaseModel):
    rowid          = AutoField()
    name           = CharField(null=False, unique=True, max_length=32)
    description    = TextField()
    created_at     = DateTimeField(default=datetime.now())
    updated_at     = DateTimeField(default=datetime.now())

class crossword_solutions(BaseModel):
    rowid          = AutoField()
    setter         = ForeignKeyField(crossword_setters)
    clue           = CharField(null=False, max_length=96)
    solution       = CharField(null=False, max_length=128)
    solution_hint  = CharField(null=False, max_length=128)
    solution_type  = ForeignKeyField(solution_types)
    created_at     = DateTimeField(default=datetime.now())
    updated_at     = DateTimeField(default=datetime.now())


"""                                             """
"""  E N D   O F   D A T A B A S E   M O D E L  """
"""                                             """
