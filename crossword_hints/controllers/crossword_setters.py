# -*- coding: utf-8 -*-
"""
Crossword setters
"""

from datetime import datetime
from peewee import fn, JOIN, DoesNotExist
from flask import request, flash, redirect, render_template
from flask_login import login_required, current_user
from crossword_hints import application
from crossword_hints.models.crossword_hints import (
    crossword_setters,
    setter_types,
    database,
)
from crossword_hints.views.crossword_hints import (
    add_log,
    Pagination,
    sanitize_input,
    get_setter_types,
)
from jur_ldap_login.models.users import Users

# from jur_ldap_login.controllers.login import load_user
# from crossword_hints.views.crossword_hints import *


@application.route("/crossword-setters/", methods=["GET"], defaults={"page": 1})
@application.route("/crossword-setters/page/<int:page>")
def crossword_setters_index(page):
    """
    Index listing of known setters
    """
    # count = crossword_setters.select(fn.COUNT(crossword_setters.rowid)).scalar()
    count = crossword_setters.select().count(database=database)
    offset = (int(page) - 1) * application.config["PER_PAGE"]
    rs = (
        crossword_setters.select(
            crossword_setters.rowid,
            crossword_setters.name,
            crossword_setters.description,
            setter_types.name.alias("setter_type_name"),
        )
        .join(setter_types)
        .where(crossword_setters.setter_type == setter_types.rowid)
        .limit(application.config["PER_PAGE"])
        .offset(offset)
        .order_by(fn.Lower(crossword_setters.name))
    )
    if not rs and page != 1:
        return (
            render_template("errors/409.html", errmsg="Requested page out of bounds"),
            409,
        )
    return render_template(
        "crossword-setters/index.html",
        setters=rs.dicts(),
        pagination=Pagination(page, application.config["PER_PAGE"], count),
        r=request,
        current_user=current_user,
    )


@application.route("/crossword-setters/<int:id>", methods=["GET"])
def crossword_setters_show(csid):
    """
    Show a new crossword setter
    """
    # Getting the setter id, name and setter_type name should be a simple inner
    # join across the tables but Peewee makes a complete mess of it by using get() which doesn't
    # seem to recognise aliases or joins.
    rs = (
        crossword_setters.select(
            crossword_setters.rowid,
            crossword_setters.name,
            crossword_setters.description,
            setter_types.name.alias("setter_type_name"),
        )
        .join(
            setter_types,
            JOIN.INNER,
            on=(crossword_setters.setter_type == setter_types.rowid),
        )
        .where(crossword_setters.rowid == csid)
        .tuples()
    )
    for rid, sname, descrip, stname in rs:
        setter = {
            "rowid": rid,
            "name": sname,
            "description": descrip,
            "setter_type_name": stname,
        }
    return render_template("crossword-setters/show.html", setter=setter, r=request)


@application.route("/crossword-setters/new", methods=["GET", "POST"])
@login_required
def crossword_setters_new():
    """
    Add a new crossword setter
    """
    if request.method == "GET":
        setter = {"name": "New setter", "setter_type_id": 1}
        return render_template(
            "crossword-setters/new.html",
            setter=setter,
            s_types=get_setter_types(),
            r=request,
            sbmt="Save new crossword setter",
        )
    rc, fdata = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "crossword-setters/new.html",
            setter=fdata,
            s_types=get_setter_types(),
            r=request,
            sbmt=request.form["submit"],
        )
    cs = crossword_setters(
        name=fdata["name"],
        setter_type_id=fdata["setter_type_id"],
        description=fdata["description"],
    )
    cs.save()
    log = (
        f"name: {fdata['name']}\nsetter_type_id: {fdata['setter_type_id']}\n"
        f"description: {fdata['description']}"
    )
    add_log(Users.get_name(current_user), "insert", "crossword_setters", cs.rowid, log)
    flash(f"Saved new crossword setter, {fdata['name']}")
    return redirect("/crossword-setters/")


@application.route("/crossword-setters/<int:id>/edit", methods=["GET", "POST"])
@login_required
def crossword_setters_edit(csid):
    """
    Edit an existing setter
    """
    if request.method == "GET":
        try:
            rs = crossword_setters.get(crossword_setters.rowid == csid)
        except DoesNotExist:
            flash(f"Cannot find crossword setter record for id, {csid}.")
            return redirect("/crossword-setters")
        rs = crossword_setters.get(crossword_setters.rowid == csid)
        return render_template(
            "crossword-setters/edit.html",
            setter=rs,
            s_types=get_setter_types(),
            r=request,
            sbmt="Update crossword setter",
        )
    rc, fdata = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "crossword-setters/edit.html",
            setter=fdata,
            r=request,
            sbmt=request.form["submit"],
        )
    cs = crossword_setters(
        rowid=csid,
        name=fdata["name"],
        setter_type_id=fdata["setter_type_id"],
        description=fdata["description"],
        updated_at=datetime.now(),
    )
    cs.save()
    log = (
        f"name: {fdata['name']}\nsetter_type_id: {fdata['setter_type_id']}\n"
        f"description: {fdata['description']}"
    )
    add_log(Users.get_name(current_user), "update", "crossword_setters", csid, log)
    flash(f"Updated crossword setter, {fdata['name']}")
    return redirect("/crossword-setters")


@application.route("/crossword-setters/<int:id>/delete", methods=["GET"])
@login_required
def crossword_setters_delete(csid):
    """
    Delete an existing setter
    """
    try:
        rs = crossword_setters.get(crossword_setters.rowid == csid)
    except DoesNotExist:
        flash(f"Cannot find crossword setter record for id, {csid}.")
        return redirect("/crossword-setters/")
    log = f"name: {rs.name}\nsetter_type_id: {rs.setter_type_id,}\ndescription: {rs.description}"
    rs.delete_instance()
    add_log(Users.get_name(current_user), "delete", "crossword_setters", csid, log)
    flash(f"Deleted crossword setter, {rs.name}")
    return redirect("/crossword-setters/")
