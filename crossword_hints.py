from flask import Flask, request, flash, redirect, render_template, g, jsonify, Response, send_file
from werkzeug import Headers
from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import Markup, escape
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
# export FLASK_APP=crossword_hints.py
# flask run
# or, with uwsgi,
# uwsgi --ini crossword_hints.ini
#
application = Flask(__name__) or create_app('crossword_hints.py')
try:
    os.environ['APP_SETTINGS']
except KeyError:
    os.environ['APP_SETTINGS'] = os.path.join(application.root_path, 'default_settings.py')

application.config.from_envvar('APP_SETTINGS')
# Create an application handle that AWS EB can understand

database = SqliteDatabase(application.config['DATABASE'], pragmas=(("foreign_keys", "on"),))
database.row_factory = sqlite3.Row

# This hook ensures that a connection is opened to handle any queries
# generated by the request.
#@application.before_request
#def _db_connect():
#    #database.get_conn()

# This hook ensures that the connection is closed when we've finished
# processing the request.
@application.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()


"""
Initialise the database - only to be used for testing and database restore
To bootstrap a database, either empty or with new schema:
$ python
>>> import crossword_hints
>>> from peewee import *
>>> with .application.app_context():
...     crossword_hints.init_db()
Params:
  None
Returns:
  None
"""
def init_db():
    #for tbl in ['setter_types', 'crossword_setters', 'solution_types', 'crossword_solutions']:
    #    database.execute_sql("drop table " + tbl)
    database.create_tables([setter_types, crossword_setters, solution_types, crossword_solutions])

@application.route('/crossword-hints/heartbeat', methods=["GET"])
def heartbeat():
    return "OK"

"""
Index listing of known solutions
Params:
  None
Returns:
  jinja2 template render of list of active requests
"""
@application.route("/crossword-solutions/")
def crossword_solution_index():
    rs = crossword_solutions.raw("""
         SELECT cs1.name as setter, cs2.solution AS solution, cs2.rowid AS csid, st1.name AS soltype
         FROM crossword_setters cs1
           INNER JOIN crossword_solutions cs2
             ON cs1.rowid = cs2.crossword_setter_id
           INNER JOIN solution_types st1
             ON cs2.solution_type_id = st1.rowid
         ORDER BY cs2.solution""")
    return(render_template('views/crossword-solutions/index.html', r=request, solns=rs))


@application.route("/crossword-solutions/<int:id>", methods=["GET"])
def crossword_solutions_show(id):
    # Getting the solution id, name and solution_type name should be a simple inner
    # join across the tables but Peewee makes a complete mess of it so it's
    # easier to do raw SQL instead.
    #rs = crossword_solutions.get(crossword_solutions.rowid, crossword_solutions.name, solution_types.name.alias('solution_type_name')).join(solution_types, JOIN.INNER).where((crossword_solutions.solution_type_id == solution_types.rowid) & (crossword_solutions.rowid == id))
    rs = crossword_solutions.raw("""
         SELECT cs1.name as setter,
                cs2.solution AS solution,
                cs2.clue AS clue,
                cs2.solution_hint AS hint,
                cs2.rowid AS csid,
                st1.name AS soltype
         FROM crossword_setters cs1
           INNER JOIN crossword_solutions cs2
             ON cs1.rowid = cs2.crossword_setter_id
           INNER JOIN solution_types st1
             ON cs2.solution_type_id = st1.rowid
         WHERE cs2.rowid = ?""", id).tuples()
    for setter, solution, clue, hint, csid, soltype in rs:
        xsol = {"csid": csid, "setter": setter, "solution": solution, "clue": clue, "hint": hint, "soltype": soltype}
    return render_template('views/crossword-solutions/show.html', soln=xsol,  r=request)

"""
Add a new crossowrd solution
"""
@application.route("/crossword-solutions/new", methods=["GET", "POST"])
def crossword_solutions_new():
    if request.method == "GET":
        solution={'clue': "Clue to the answer",
                  'solution': 'Thesolution',
                  'solution_hint': 'New solution hint',
                  'crossword_setter_id': 1,
                  'solution_type_id': 1}
        return render_template('views/crossword-solutions/new.html', soln=solution, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt='Save new crossword solution')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/crossword-solutions/new.html', soln=fdata, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt=request.form['submit']))
    cs = crossword_solutions(crossword_setter_id=fdata['crossword_setter_id'],
                             clue=fdata['clue'],
                             solution=fdata['solution'],
                             solution_hint=fdata['solution_hint'],
                             solution_type_id=fdata['solution_type_id'],
                             created_at=datetime.now(),
                             updated_at=datetime.now())
    cs.save()
    flash("Saved new crossword solution, %s" % fdata['solution'])
    return redirect('/crossword-solutions/')

"""
Edit an existing solution
"""
@application.route("/crossword-solutions/<int:id>/edit", methods=["GET", "POST"])
def crossword_solutions_edit(id):
    if request.method == "GET":
        try:
            rs = crossword_solutions.get(crossword_solutions.rowid == id)
        except DoesNotExist:
            flash("Cannot find crossword solution record for id, %s." % id)
            return(redirect('/crossword-solutions'))
        return render_template('views/crossword-solutions/edit.html', soln=rs, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt='Update crossword solution')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/crossword-solutions/edit.html', solution=fdata, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt=request.form['submit']))
    cs = crossword_solutions(rowid=id,
                             crossword_setter_id=fdata['crossword_setter_id'],
                             clue=fdata['clue'],
                             solution=fdata['solution'],
                             solution_hint=fdata['solution_hint'],
                             solution_type_id=fdata['solution_type_id'],
                             updated_at=datetime.now())
    cs.save()
    flash("Updated crossword solution, %s" % fdata['solution'])
    return(redirect('/crossword-solutions'))

@application.route("/crossword-solutions/<int:id>/delete", methods=["GET"])
def crossword_solutions_delete(id):
    try:
        rs = crossword_solutions.get(crossword_solutions.rowid == id)
    except DoesNotExist:
        flash("Cannot find solution record for id, %s." % id)
        return(redirect('/crossword-solutions'))
    rs.delete_instance()
    flash("Deleted crossword solution, %s" % rs.solution)
    return(redirect('/crossword-solutions'))

"""                                                   """
"""   C  R  O  S  S  W  O  R  D      H  I  N  T  S    """
"""                                                   """
@application.route("/crossword-hints/", methods=["GET", "POST"], defaults={'path': ''})
@application.route('/', methods=["GET", "POST"], defaults={'path': ''})
def crossowrd_hints_index(path):
    if request.method == "GET":
        return(render_template('views/crossword-hints/index.html', r=request))
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/crossword-hints/index.html', r=request, sbmt=request.form['submit']))
    # Ideally, peewee would allow the selection of the columns from the joined
    # tables but it doesn't seem to recognise them despite what might be in the
    # documentation. So we have to perform separate lookups for the solution
    # type and setter
    #rs = crossword_solutions.select(crossword_solutions.clue, crossword_solutions.solution, crossword_solutions.solution_hint, solution_types.name.alias("soltype"), crossword_setters.name.alias("setter")) \
    #                          .join(solution_types, JOIN.INNER, on=(crossword_solutions.solution_type_id == solution_types.rowid)) \
    #                          .switch(crossword_solutions) \
    #                          .join(crossword_setters, JOIN.INNER, on=(crossword_solutions.crossword_setter_id == crossword_setters.rowid)) \
    #                          .where(crossword_solutions.clue.contains(fdata['cue_word']))
    #rs = crossword_solutions.select().where(crossword_solutions.clue.contains(fdata['cue_word']))
    # A raw query gives it all in one
    rs = crossword_solutions.raw("""
SELECT cs1.name as setter, cs2.solution AS solution, cs2.clue AS clue,
       cs2.solution_hint AS hint, cs2.rowid AS csid, st1.name AS soltype
         FROM crossword_setters cs1
           INNER JOIN crossword_solutions cs2
             ON cs1.rowid = cs2.crossword_setter_id
           INNER JOIN solution_types st1
             ON cs2.solution_type_id = st1.rowid
WHERE cs2.clue LIKE ?
ORDER BY cs2.solution;
    """, '%{0}%'.format(fdata['cue_word']))
    clueset = []
    for row in rs:
        clueset.append({"clue": row.clue, "solution": row.solution, "hint": row.hint, "soltype": row.soltype, "setter": row.setter })
    return(render_template('views/crossword-hints/index.html', r=request, clues=clueset))

"""                                                    """
""" Search database for cue words matching search term """
""" JQuery is used to handle an AJAX request to search """
""" the database for a matching cue word. This submits """
""" via a GET request with a callback reference that   """
""" needs to be included in the response in JSONP      """
"""                                                    """
@application.route("/cue-words/", methods=["GET"])
def crossword_cue_search():
    callback = request.args.get('callback')
    if not callback or callback == "":
        return(render_template('errors/409.html', errmsg="Missing JQuery callback value"), 400)
    rs = cue_words.select(cue_words.rowid, cue_words.cue_word).where(cue_words.cue_word.contains(request.args['cue']))
    ary = {}
    for row in rs:
        ary[row.rowid] = row.cue_word
    ret = '{0}({1})'.format(callback, json.dumps(ary))
    return(Response(ret, mimetype="text/json"))

"""
Index listing of known setters
"""
@application.route("/crossword-setters/", methods=["GET"])
def crossword_setters_index():
    rs = crossword_setters.select(crossword_setters.rowid, crossword_setters.name, crossword_setters.description, setter_types.name.alias('setter_type_name')).join(setter_types).where(crossword_setters.setter_type_id == setter_types.rowid)
    return render_template('views/crossword-setters/index.html', setters=rs.dicts(), r=request)

@application.route("/crossword-setters/<int:id>", methods=["GET"])
def crossword_setters_show(id):
    # Getting the setter id, name and setter_type name should be a simple inner
    # join across the tables but Peewee makes a complete mess of it so it's
    # easier to do raw SQL instead.
    #rs = crossword_setters.get(crossword_setters.rowid, crossword_setters.name, setter_types.name.alias('setter_type_name')).join(setter_types, JOIN.INNER).where((crossword_setters.setter_type_id == setter_types.rowid) & (crossword_setters.rowid == id))
    rs = crossword_setters.raw('SELECT t1.name, t1.description, t2.name AS setter_type_name FROM crossword_setters t1 INNER JOIN setter_types t2 ON t1.setter_type_id = t2.rowid  AND t1.rowid = ?', id).tuples()
    for sname, descrip, stname in rs:
        stype = {"rowid": id, "name": sname, "description": descrip, "setter_type_name": stname}
    return render_template('views/crossword-setters/show.html', stype=stype,  r=request)

"""
Add a new crossword setter
"""
@application.route("/crossword-setters/new", methods=["GET", "POST"])
def crossword_setters_new():
    if request.method == "GET":
        setter={'name': "New setter", 'setter_type_id': 1}
        return render_template('views/crossword-setters/new.html', setter=setter, s_types=get_setter_types(), r=request, sbmt='Save new crossword setter')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/crossword-setters/new.html', setter=fdata, s_types=get_setter_types(), r=request, sbmt=request.form['submit']))
    st = crossword_setters(name=fdata['name'], setter_type_id=fdata['setter_type_id'], description=fdata['description'])
    st.save()
    flash("Saved new crossword setter, %s" % fdata['name'])
    return redirect('/crossword-setters/')

"""
Edit an existing setter
"""
@application.route("/crossword-setters/<int:id>/edit", methods=["GET", "POST"])
def crossword_setters_edit(id):
    if request.method == "GET":
        try:
            rs = crossword_setters.get(crossword_setters.rowid == id)
        except DoesNotExist:
            flash("Cannot find crossword setter record for id, %s." % id)
            return(redirect('/crossword-setters'))
        rs = crossword_setters.get(crossword_setters.rowid == id)
        return render_template('views/crossword-setters/edit.html', setter=rs, s_types=get_setter_types(), r=request, sbmt='Update crossword setter')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/crossword-setters/edit.html', setter=fdata, r=request, sbmt=request.form['submit']))
    cs = crossword_setters(rowid=id, name=fdata['name'],
                           setter_type_id=fdata['setter_type_id'],
                           description=fdata['description'],
                           updated_at=datetime.now())
    cs.save()
    flash("Updated crossword setter, %s" % fdata['name'])
    return(redirect('/crossword-setters'))

"""
Delete an existing setter
"""
@application.route("/crossword-setters/<int:id>/delete", methods=["GET"])
def crossword_setters_delete(id):
    try:
        rs = crossword_setters.get(crossword_setters.rowid == id)
    except DoesNotExist:
        flash("Cannot find crssword setter record for id, %s." % id)
        return(redirect('/crossword-setters/'))
    rs.delete_instance()
    flash("Deleted crossword setter, %s" % rs.name)
    return(redirect('/crossword-setters/'))

"""              """
""" Setter types """
"""              """
@application.route("/setter-types/", methods=["GET"])
def setter_types_index():
    rs = setter_types.select()
    return render_template('views/setter-types/index.html', stypes=rs.dicts(), r=request)

@application.route("/setter-types/<int:id>", methods=["GET"])
def setter_types_show(id):
    rs = setter_types.get(setter_types.rowid == id)
    return render_template('views/setter-types/show.html', stype=rs,  r=request)

@application.route("/setter-types/new", methods=["GET", "POST"])
def setter_types_new():
    if request.method == "GET":
        stype={'name': "New setter type", 'description': 'Brief description of this type of setter'}
        return(render_template('views/setter-types/new.html', stype=stype,  r=request, sbmt='Save new setter type'))
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/setter-types/new.html', stype=fdata, r=request, sbmt=request.form['submit']))
    st = setter_types(name=fdata['name'], description=fdata['description'])
    st.save()
    flash("Saved new setter type, %s" % fdata['name'])
    return redirect('/setter-types')


@application.route("/setter-types/<int:id>/edit", methods=["GET", "POST"])
def setter_types_edit(id):
    if request.method == "GET":
        try:
            rs = setter_types.get(setter_types.rowid == id)
        except DoesNotExist:
            flash("Cannot find setter type record for id, %s." % id)
            return(redirect('/setter-types'))
        return(render_template('views/setter-types/edit.html', stype=rs, r=request, sbmt='Update setter type'))
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/setter-types/edit.html', stype=fdata, r=request, sbmt=request.form['submit']))
    st = setter_types(rowid=id, name=fdata['name'],
                      description=fdata['description'],
                      updated_at=datetime.now())
    st.save()
    flash("Updated setter type, %s" % fdata['name'])
    return(redirect('/setter-types'))

@application.route("/setter-types/<int:id>/delete", methods=["GET"])
def setter_types_delete(id):
    try:
        rs = setter_types.get(setter_types.rowid == id)
    except DoesNotExist:
        flash("Cannot find setter type record for id, %s." % id)
        return(redirect('/setter-types'))
    rs.delete_instance()
    flash("Deleted setter type, %s" % rs.name)
    return(redirect('/setter-types'))


"""               """
""" Solution types """
"""               """
@application.route("/solution-types/", methods=["GET"])
def solution_types_index():
    rs = solution_types.select()
    return render_template('views/solution-types/index.html', stypes=rs.dicts(), r=request)

@application.route("/solution-types/<int:id>", methods=["GET"])
def solution_types_show(id):
    rs = solution_types.get(solution_types.rowid == id)
    return render_template('views/solution-types/show.html', stype=rs,  r=request)

@application.route("/solution-types/new", methods=["GET", "POST"])
def solution_types_new():
    if request.method == "GET":
        stype={'name': "New solution type", 'description': 'Brief description of this type of solution'}
        return render_template('views/solution-types/new.html', stype=stype,  r=request, sbmt='Save new solution type')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/solution-types/new.html', stype=fdata, r=request, sbmt=request.form['submit']))
    st = solution_types(name=fdata['name'], description=fdata['description'])
    st.save()
    flash("Saved new solution type, %s" % fdata['name'])
    return redirect('/solution-types')

@application.route("/solution-types/<int:id>/edit", methods=["GET", "POST"])
def solution_types_edit(id):
    try:
        stype = solution_types.get(solution_types.rowid == id)
    except DoesNotExist:
        flash("Cannot find solution type record for id, %s." % id)
        return(redirect('/solution-types'))
    if request.method == "GET":
        return render_template('views/solution-types/new.html', stype=stype,  r=request, sbmt='Update solution type')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/solution-types/edit.html', stype=fdata, r=request, sbmt=request.form['submit']))
    st = solution_types(rowid=id, name=fdata['name'],
                      description=fdata['description'],
                      updated_at=datetime.now())
    st.save()
    flash("Updated solution type, %s" % fdata['name'])
    return(redirect('/solution-types'))

@application.route("/solution-types/<int:id>/delete", methods=["GET", "POST"])
def solution_types_delete(id):
    try:
        rs = solution_types.get(solution_types.rowid == id)
    except DoesNotExist:
        flash("Cannot find solution type record for id, %s." % id)
        return(redirect('/solution-types'))
    rs.delete_instance()
    flash("Deleted solution type, %s" % rs.name)
    return(redirect("/solution-types"))


"""                                                        """
"""  E  X  C  E  P  T  I  O  N    H  A  N  D  L  I  N  G   """
"""                                                        """
@application.errorhandler(DoesNotExist)
def handle_database_error(error):
    return(render_template('errors/409.html', errmsg=error), 409)
@application.errorhandler(409)
def handle_database_error(error):
    return(render_template('errors/409.html', errmsg=error), 409)
@application.errorhandler(OperationalError)
def handle_opertional_error(error):
    return(render_template('errors/409.html', errmsg=error), 409)
@application.errorhandler(404)
def handle_opertional_error(error):
    return(render_template('errors/404.html', errmsg=error))
@application.errorhandler(500)
def handle_opertional_error(error):
    return(render_template('errors/500.html', errmsg=error))

"""                                                        """
"""  I  N  T  E  R  N  A  L    F  U  N  C  T  I  O  N  S   """
"""                                                        """
"""
Construct an array containing the setter_type rowid and name
suitable for use in a SELECT form element
"""
def get_setter_types():
    rs=setter_types.select(setter_types.rowid, setter_types.name)
    s_types = []
    for row in rs.dicts():
        s_types.append([row['rowid'], row['name']])
    return(s_types)

"""
Construct an array containing the crossword setter rowid and name
suitable for use in a SELECT form element
"""
def get_crossword_setters():
    cs=crossword_setters.select(crossword_setters.rowid, crossword_setters.name)
    setters = []
    for row in cs.dicts():
        setters.append([row['rowid'], row['name']])
    return(setters)

"""
Construct an array containing the solution_type rowid and name
suitable for use in a SELECT form element
"""
def get_solution_types():
    rs=solution_types.select(solution_types.rowid, solution_types.name)
    s_types = []
    for row in rs.dicts():
        s_types.append([row['rowid'], row['name']])
    return(s_types)

"""
Basic attempt to sanitize submitted form data
Attempt to validate all elements in the form data but if ny one element
is bd make sure the whole form is invalidated.
"""
def sanitize_input(form):
    data = {}
    rc = ""
    for elem in request.form:
        if elem == "name":
            (r, data[elem]) = validate_name(form[elem])
        elif re.match(r'^.*_id$', elem):
            (r, data[elem]) = validate_id(form[elem])
        else:
            (r, data[elem]) = validate_text(form[elem])
        if rc == "": rc = r
    return(rc, data)


def validate_name(str):
    if not re.match(r'^[a-zA-Z0-9-_.\' ()]*$', str):
        return("Invalid characters in name field: Only allowed a-zA-Z0-9-_. '", re.sub('[^a-zA-Z0-9-_\'. ]', "", str))
    return("", str)

def validate_text(str):
    return("", str)

"""
We expect submitted id values to be numeric
"""
def validate_id(str):
    try:
        int(str)
    except ValueError:
        return("id values must be numeric", "0")
    return("", str)

"""
Need to calculate the next rowid value for a table
"""
def nextId(tbl):
    return(database.execute_sql("SELECT MAX(rowid)+1 FROM %s" % tbl),scalar())

"""                                                        """
"""  D  A  T  A  B  A  S  E     M  O  D  E  L  L  I  N  G  """
"""                                                        """
"""                                                        """
"""     A base model that will use our Sqlite database.    """
"""     Appears to be incompatible with Flask TestCase     """
class BaseModel(Model):
    with application.app_context():
        class Meta:
            database = database

class activity_logs(BaseModel):
    rowid            = AutoField()
    action           = CharField(max_length=32)
    item             = CharField(max_length=32)
    item_id          = IntegerField()
    activity         = TextField()
    updated_by       = CharField(max_length=32)
    updated_at       = DateTimeField(default=datetime.now())

class setter_types(BaseModel):
    rowid            = AutoField()
    name             = CharField(null=False, max_length=16, unique=True)
    description      = TextField()
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class crossword_setters(BaseModel):
    rowid            = AutoField()
    name             = CharField(null=False, unique=True, max_length=32)
    setter_type      = ForeignKeyField(setter_types)
    description      = TextField()
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class solution_types(BaseModel):
    rowid            = AutoField()
    name             = CharField(null=False, unique=True, max_length=32)
    description      = TextField()
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class crossword_solutions(BaseModel):
    rowid            = AutoField()
    crossword_setter = ForeignKeyField(crossword_setters)
    clue             = CharField(null=False, max_length=96)
    solution         = CharField(null=False, max_length=128)
    solution_hint    = CharField(null=False, max_length=128)
    solution_type    = ForeignKeyField(solution_types)
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class cue_words(BaseModel):
    rowid            = AutoField()
    cue_word         = CharField(null=False, max_length=32)
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

"""                                             """
"""  E N D   O F   D A T A B A S E   M O D E L  """
"""                                             """
