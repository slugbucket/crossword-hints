# -*- coding: utf-8 -*-
from crossword_hints import application
from crossword_hints.models.crossword_hints import setter_types
from jur_ldap_login.models.users import users
from jur_ldap_login.controllers.login import load_user
from flask import request, flash, redirect, render_template
from flask_login import login_required, current_user
from peewee import *
from datetime import date, timedelta, datetime
from crossword_hints.views.crossword_hints import *

"""              """
""" Setter types """
"""              """
@application.route("/setter-types/", methods=["GET"], defaults={'page': 1})
@application.route('/setter-types/page/<int:page>')
def setter_types_index(page):
    count = setter_types.select(fn.COUNT(setter_types.rowid)).scalar()
    offset = ((int(page)-1) * application.config['PER_PAGE'])
    rs = setter_types.select().limit(application.config['PER_PAGE']).offset(offset).order_by(fn.Lower(setter_types.name))
    if not rs and page != 1:
        return(render_template('errors/409.html', errmsg="Requested page out of bounds"), 409 )
    return render_template('setter-types/index.html',
                           stypes=rs.dicts(),
                           pagination=Pagination(page, application.config['PER_PAGE'], count),
                           r=request)

@application.route("/setter-types/<int:id>", methods=["GET"])
def setter_types_show(id):
    rs = setter_types.get(setter_types.rowid == id)
    return render_template('setter-types/show.html', stype=rs,  r=request)

@application.route("/setter-types/new", methods=["GET", "POST"])
@login_required
def setter_types_new():
    if request.method == "GET":
        stype={'name': "New setter type", 'description': 'Brief description of this type of setter'}
        return(render_template('setter-types/new.html', stype=stype,  r=request, sbmt='Save new setter type'))
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('setter-types/new.html', stype=fdata, r=request, sbmt=request.form['submit']))
    st = setter_types(name=fdata['name'], description=fdata['description'])
    st.save()
    log = ("name: %s\ndescription: %s" % (fdata['name'], fdata['description']))
    add_log(users.get_name(current_user), 'insert', 'setter_types', st.rowid, log)
    flash("Saved new setter type, %s" % fdata['name'])
    return redirect('/setter-types')


@application.route("/setter-types/<int:id>/edit", methods=["GET", "POST"])
@login_required
def setter_types_edit(id):
    if request.method == "GET":
        try:
            rs = setter_types.get(setter_types.rowid == id)
        except DoesNotExist:
            flash("Cannot find setter type record for id, %s." % id)
            return(redirect('/setter-types'))
        return(render_template('setter-types/edit.html', stype=rs, r=request, sbmt='Update setter type'))
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('setter-types/edit.html', stype=fdata, r=request, sbmt=request.form['submit']))
    st = setter_types(rowid=id, name=fdata['name'],
                      description=fdata['description'],
                      updated_at=datetime.now())
    st.save()
    log = ("name: %s\ndescription: %s" % (fdata['name'], fdata['description']))
    add_log(users.get_name(current_user), 'update]', 'setter_types', id, log)
    flash("Updated setter type, %s" % fdata['name'])
    return(redirect('/setter-types'))

@application.route("/setter-types/<int:id>/delete", methods=["GET"])
@login_required
def setter_types_delete(id):
    try:
        rs = setter_types.get(setter_types.rowid == id)
    except DoesNotExist:
        flash("Cannot find setter type record for id, %s." % id)
        return(redirect('/setter-types'))
    log = ("name: %s\ndescription: %s" % (rs.name, rs.description))
    rs.delete_instance()
    add_log(users.get_name(current_user), 'delete', 'setter_types', rs.rowid, log)
    flash("Deleted setter type, %s" % rs.name)
    return(redirect('/setter-types'))