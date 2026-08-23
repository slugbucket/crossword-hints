# -*- coding: utf-8 -*-
"""
Setter types
"""
# from crossword_hints import application
# from crossword_hints.models.crossword_hints import setter_types
# from jur_ldap_login.controllers.login import load_user
from datetime import datetime
from flask import request, flash, redirect, render_template
from peewee import fn, DoesNotExist
from flask_login import login_required, current_user
# from crossword_hints.views.crossword_hints import *
from crossword_hints.models.crossword_hints import database, setter_types
from crossword_hints.views.crossword_hints import Pagination
from crossword_hints import application, sanitize_input, add_log
from jur_ldap_login.models.users import users


@application.route("/setter-types/", methods=["GET"], defaults={"page": 1})
@application.route("/setter-types/page/<int:page>")
def setter_types_index(page):
    """
    Setter types index route
    """
    # count = setter_types.select(fn.COUNT(setter_types.rowid)).scalar()
    count = setter_types.select().count(database=database)
    offset = (int(page) - 1) * application.config["PER_PAGE"]
    rs = (
        setter_types.select()
        .limit(application.config["PER_PAGE"])
        .offset(offset)
        .order_by(fn.Lower(setter_types.name))
    )
    if not rs and page != 1:
        return (
            render_template(
                "errors/409.html",
                errmsg="Requested page out of bounds",
            ),
            409,
        )
    return render_template(
        "setter-types/index.html",
        stypes=rs.dicts(),
        pagination=Pagination(page, application.config["PER_PAGE"], count),
        r=request,
    )


@application.route("/setter-types/<int:id>", methods=["GET"])
def setter_types_show(rowid):
    """
    Setter types show route
    """
    rs = setter_types.get(setter_types.rowid == rowid)
    return render_template("setter-types/show.html", stype=rs, r=request)


@application.route("/setter-types/new", methods=["GET", "POST"])
@login_required
def setter_types_new():
    """
    Setter types new route
    """
    if request.method == "GET":
        stype = {
            "name": "New setter type",
            "description": "Brief description of this type of setter",
        }
        return render_template(
            "setter-types/new.html", stype=stype, r=request, sbmt="Save new setter type"
        )
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "setter-types/new.html", stype=fdata, r=request, sbmt=request.form["submit"]
        )
    st = setter_types(name=fdata["name"], description=fdata["description"])
    st.save()
    log = f"name: {fdata['name']}\ndescription: {fdata['description']}"
    add_log(users.get_name(current_user), "insert", "setter_types", st.rowid, log)
    flash(f"Saved new setter type, {fdata['name']}")
    return redirect("/setter-types")


@application.route("/setter-types/<int:id>/edit", methods=["GET", "POST"])
@login_required
def setter_types_edit(stid):
    """
    Setter types edit route
    """
    if request.method == "GET":
        try:
            rs = setter_types.get(setter_types.rowid == stid)
        except DoesNotExist:
            flash(f"Cannot find setter type record for id, {stid}.")
            return redirect("/setter-types")
        return render_template(
            "setter-types/edit.html", stype=rs, r=request, sbmt="Update setter type"
        )
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "setter-types/edit.html",
            stype=fdata,
            r=request,
            sbmt=request.form["submit"],
        )
    st = setter_types(
        rowid=stid,
        name=fdata["name"],
        description=fdata["description"],
        updated_at=datetime.now(),
    )
    st.save()
    log = f"name: {fdata['name']}\ndescription: {fdata['description']}"
    add_log(users.get_name(current_user), "update]", "setter_types", stid, log)
    flash(f"Updated setter type, {fdata['name']}")
    return redirect("/setter-types")


@application.route("/setter-types/<int:id>/delete", methods=["GET"])
@login_required
def setter_types_delete(stid):
    """
    Setter types delete route
    """
    try:
        rs = setter_types.get(setter_types.rowid == stid)
    except DoesNotExist:
        flash(f"Cannot find setter type record for id, {stid}.")
        return redirect("/setter-types")
    log = f"name: {rs.name}\ndescription: {rs.description}"
    rs.delete_instance()
    add_log(users.get_name(current_user), "delete", "setter_types", rs.rowid, log)
    flash(f"Deleted setter type, {rs.name}")
    return redirect("/setter-types")
