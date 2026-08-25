# -*- coding: utf-8 -*-
"""
Crossword solution types
"""

from datetime import datetime
from peewee import fn, DoesNotExist
from flask import request, flash, redirect, render_template, jsonify
from flask_login import login_required, current_user
from crossword_hints import application, logger
from crossword_hints.models.crossword_hints import solution_types, database
from crossword_hints.views.crossword_hints import add_log, Pagination, sanitize_input
from jur_ldap_login.models.users import Users

# from jur_ldap_login.controllers.login import load_user
# from crossword_hints.views.crossword_hints import *


@application.route("/solution-types/", methods=["GET"], defaults={"page": 1})
@application.route("/solution-types/page/<int:page>")
def solution_types_index(page):
    """
    Solution types index
    """
    # count = solution_types.select(fn.COUNT(solution_types.rowid)).scalar()
    count = solution_types.select().count(database=database)
    offset = (int(page) - 1) * application.config["PER_PAGE"]
    rs = (
        solution_types.select()
        .limit(application.config["PER_PAGE"])
        .offset(offset)
        .order_by(fn.Lower(solution_types.name))
    )
    if not rs and page != 1:
        return (
            render_template(
                "errors/409.html",
                errmsg="Requested page out of bounds",
            ),
            409,
        )
    logger.debug(
        "solution_types_index: page=%s, count=%s, offset=%s", page, count, offset
    )
    return render_template(
        "solution-types/index.html",
        stypes=rs.dicts(),
        pagination=Pagination(page, application.config["PER_PAGE"], count),
        r=request,
    )


@application.route("/solution-types/index.ajax.html", methods=["GET"])
def solution_types_index_ajax():
    """
    Route for direct rendering of the solution-types table in response to an AJAX request
    """
    rs = solution_types.select().order_by(fn.Lower(solution_types.name))
    return render_template("solution-types/_index.ajax.html", stypes=rs.dicts())


@application.route("/solution-types/index.json", methods=["GET"])
def solution_types_index_json():
    """
    Solution types JSON route for AJAX requests
    """
    rs = solution_types.select().order_by(fn.Lower(solution_types.name)).dicts()
    if not rs:
        return jsonify({"result": "error"})
    res = []
    for row in rs:
        res.append(dict(row))
    return jsonify(res)


@application.route("/solution-types/<int:stid>", methods=["GET"])
def solution_types_show(stid):
    """
    Render a template of the detail of a spefic solution type
    """
    rs = solution_types.get(solution_types.rowid == stid)
    return render_template("solution-types/show.html", stype=rs, r=request)


@application.route("/solution-types/new", methods=["GET", "POST"])
@login_required
def solution_types_new():
    """
    Display a form requesting the details of a new solution type
    """
    if request.method == "GET":
        stype = {
            "name": "New solution type",
            "description": "Brief description of this type of solution",
        }
        return render_template(
            "solution-types/new.html",
            stype=stype,
            r=request,
            sbmt="Save new solution type",
        )
    rc, fdata = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "solution-types/new.html",
            stype=fdata,
            r=request,
            sbmt=request.form["submit"],
        )
    st = solution_types(name=fdata["name"], description=fdata["description"])
    st.save()
    log = f"name: {fdata['name']}\ndescription: {fdata['description']}"
    add_log(Users.get_name(current_user), "insert", "solution_types", st.rowid, log)
    flash(f"Saved new solution type, {fdata['name']}")
    return redirect("/solution-types")


@application.route("/solution-types/<int:stid>/edit", methods=["GET", "POST"])
@login_required
def solution_types_edit(stid):
    """
    Display a form to edit the details of an existing solution type
    """
    try:
        stype = solution_types.get(solution_types.rowid == stid)
    except DoesNotExist:
        flash(f"Cannot find solution type record for id, {stid}.")
        return redirect("/solution-types")
    if request.method == "GET":
        return render_template(
            "solution-types/new.html",
            stype=stype,
            r=request,
            sbmt="Update solution type",
        )
    rc, fdata = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "solution-types/edit.html",
            stype=fdata,
            r=request,
            sbmt=request.form["submit"],
        )
    st = solution_types(
        rowid=stid,
        name=fdata["name"],
        description=fdata["description"],
        updated_at=datetime.now(),
    )
    st.save()
    log = f"name: {fdata['name']}\ndescription: {fdata['description']}"
    add_log(Users.get_name(current_user), "update", "solution_types", stid, log)
    flash(f"Updated solution type, {fdata['name']}")
    return redirect("/solution-types")


@application.route("/solution-types/<int:stid>/delete", methods=["GET", "POST"])
@login_required
def solution_types_delete(stid):
    """
    Delete an existing solution type
    """
    try:
        rs = solution_types.get(solution_types.rowid == stid)
    except DoesNotExist:
        flash(f"Cannot find solution type record for id, {stid}.")
        return redirect("/solution-types")
    log = f"name: {rs.name}\ndescription: {rs.description}"
    rs.delete_instance()
    add_log(Users.get_name(current_user), "delete", "solution_types", rs.rowid, log)
    flash(f"Deleted solution type, {rs.name}")
    return redirect("/solution-types")
