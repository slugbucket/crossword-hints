# -*- coding: utf-8 -*-
from crossword_hints import application
from crossword_hints.models.crossword_hints import cue_words
from jur_ldap_login.models.users import users
from jur_ldap_login.controllers.login import load_user
from flask import request, redirect, Response, render_template
import json
from flask_login import login_required, current_user
from peewee import *
from crossword_hints.views.crossword_hints import sanitize_input

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
    rs = cue_words.select(cue_words.cue_word).where(cue_words.cue_word.contains(request.args['cue'])).distinct()
    ary = []
    for row in rs:
        ary.append(row.cue_word)
    ret = '{0}({1})'.format(callback, json.dumps(ary))
    return(Response(ret, mimetype="text/json"))

"""
Submit a new cue word to the database
"""
@application.route("/cue-words/new", methods=["GET", "POST"])
@login_required
def crossword_cue_new():
    if request.method == "GET":
        cue={'cue_word': "Cue word",
             'meaning':  "Cue meaning"}
        return render_template('cue-words/new.html', cue=cue, r=request, sbmt='Save new cue word')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('cue-words/new.html', cue=fdata, r=request, sbmt=request.form['submit']))
    cw = cue_words(cue_word=fdata['cue_word'], meaning=fdata['meaning'])
    cw.save()
    return(redirect('/crossword-hints'))
