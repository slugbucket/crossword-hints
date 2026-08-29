# -*- coding: utf-8 -*-
"""
Crossword solutions
"""

from datetime import datetime
import re
from flask import request, flash, redirect, render_template, session
from flask_login import login_required, current_user
from peewee import fn, JOIN, DoesNotExist
from crossword_hints import application
import crossword_hints.models.crossword_hints
from crossword_hints.views.crossword_hints import (
    add_log,
    Pagination,
    sanitize_input,
    get_crossword_setters,
    get_solution_types,
)
from jur_oauth2_login.models.users import Users


@application.route("/crossword-solutions/", defaults={"page": 1})
@application.route("/crossword-solutions/page/<int:page>")
@application.route(
    "/crossword-solutions/search", methods=["POST"], defaults={"page": 1}
)
def crossword_solution_index(page):
    """
    Index listing of known solutions
    Params:
      page: int for the page number of results to display
    Returns:
      jinja2 template render of list of retrieved solutions
    """
    if "solutions_page" not in session:
        session["solutions_page"] = page
    else:  # "solutions_page" in session
        if re.match(r"^.*/crossword-solutions.*", request.referrer):
            session["solutions_page"] = page
            # print(f"Came from other solutions page, update the session['solutions_page'] to {page}")
        #else:  # useful for debugging, but not needed in production
        #    pass
        #    print(f"clicked on solutions link, page = {page} with session['solutions_page'] = {session['solutions_page']}. Do nothing.")
    page_num = session["solutions_page"]

    term = ""
    # JUR: This can most likely be removed as it is not used anywhere.
    # qtrm = "%"
    if request.method == "POST":
        _, fdata = sanitize_input(request.form)
        term = fdata["search_box"]
        # qtrm = "%" + term + "%"
        page_num = 1
    else:
        if request.args.get("q"):
            term = request.args.get("q")
            # qtrm = "%" + term + "%"

    rs = (
        crossword_hints.models.crossword_hints.crossword_setters.select(
            crossword_hints.models.crossword_hints.crossword_solutions.rowid.alias(
                "csid"
            ),
            crossword_hints.models.crossword_hints.crossword_solutions.solution,
            crossword_hints.models.crossword_hints.crossword_solutions.clue,
            crossword_hints.models.crossword_hints.solution_types.name.alias("soltype"),
            crossword_hints.models.crossword_hints.crossword_setters.name.alias(
                "setter"
            ),
        )
        .join(
            crossword_hints.models.crossword_hints.crossword_solutions,
            JOIN.INNER,
            on=(
                crossword_hints.models.crossword_hints.crossword_setters.rowid
                == crossword_hints.models.crossword_hints.crossword_solutions.crossword_setter
            ),
        )
        .join(
            crossword_hints.models.crossword_hints.solution_types,
            JOIN.INNER,
            on=(
                crossword_hints.models.crossword_hints.crossword_solutions.solution_type
                == crossword_hints.models.crossword_hints.solution_types.rowid
            ),
        )
        .where(
            crossword_hints.models.crossword_hints.crossword_solutions.solution.contains(
                term
            )
            | crossword_hints.models.crossword_hints.crossword_setters.name.contains(
                term
            )
            | crossword_hints.models.crossword_hints.solution_types.name.contains(term)
        )
        .order_by(
            fn.Lower(
                crossword_hints.models.crossword_hints.crossword_solutions.solution
            )
        )
        .dicts()
    )
    count = len(rs)
    # offset = (page_num - 1) * application.config["PER_PAGE"]
    # Display a 409 not found page for out of bounds request, but no error for emmpty result set
    try:
        solutions = rs.paginate(page_num, application.config["PER_PAGE"])
    except DoesNotExist:
        session.pop("solutions_page")
        return (
            render_template("errors/409.html", errmsg="Requested page out of bounds"),
            409,
        )
    return render_template(
        "crossword-solutions/index.html",
        r=request,
        solns=solutions,
        pagination=Pagination(page_num, application.config["PER_PAGE"], count),
        search_term=term,
    )


@application.route("/crossword-solutions/<int:csid>", methods=["GET"])
def crossword_solutions_show(csid):
    """
    Display an existing solution
    """
    rs = (
        crossword_hints.models.crossword_hints.crossword_setters.select(
            crossword_hints.models.crossword_hints.crossword_solutions.rowid.alias(
                "csid"
            ),
            crossword_hints.models.crossword_hints.crossword_solutions.solution,
            crossword_hints.models.crossword_hints.crossword_solutions.clue,
            crossword_hints.models.crossword_hints.crossword_solutions.solution_hint.alias(
                "hint"
            ),
            crossword_hints.models.crossword_hints.solution_types.name.alias("soltype"),
            crossword_hints.models.crossword_hints.crossword_setters.name.alias(
                "setter"
            ),
        )
        .join(
            crossword_hints.models.crossword_hints.crossword_solutions,
            JOIN.INNER,
            on=(
                crossword_hints.models.crossword_hints.crossword_setters.rowid
                == crossword_hints.models.crossword_hints.crossword_solutions.crossword_setter
            ),
        )
        .join(
            crossword_hints.models.crossword_hints.solution_types,
            JOIN.INNER,
            on=(
                crossword_hints.models.crossword_hints.crossword_solutions.solution_type
                == crossword_hints.models.crossword_hints.solution_types.rowid
            ),
        )
        .where(crossword_hints.models.crossword_hints.crossword_solutions.rowid == csid)
        .order_by(
            fn.Lower(
                crossword_hints.models.crossword_hints.crossword_solutions.solution
            )
        )
        .tuples()
    )
    for solid, solution, clue, hint, soltype, setter in rs:
        xsol = {
            "csid": solid,
            "setter": setter,
            "solution": solution,
            "clue": clue,
            "hint": hint,
            "soltype": soltype,
        }
    return render_template("crossword-solutions/show.html", soln=xsol, r=request)


@application.route("/crossword-solutions/new", methods=["GET", "POST"])
@login_required
def crossword_solutions_new():
    """
    Add a new crossowrd solution
    """
    if request.method == "GET":
        setter_id = 1 if "setter_id" not in session else session["setter_id"]
        solution = {
            "clue": "Clue to the answer",
            "solution": "Thesolution",
            "solution_hint": "New solution hint",
            "crossword_setter_id": setter_id,
            "solution_type_id": 1,
        }
        return render_template(
            "crossword-solutions/new.html",
            soln=solution,
            s_types=get_solution_types(),
            setters=get_crossword_setters(),
            r=request,
            sbmt="Save new crossword solution",
        )
    rc, fdata = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "crossword-solutions/new.html",
            soln=fdata,
            s_types=get_solution_types(),
            setters=get_crossword_setters(),
            r=request,
            sbmt=request.form["submit"],
        )
    cs = crossword_hints.models.crossword_hints.crossword_solutions(
        crossword_setter_id=fdata["crossword_setter_id"],
        clue=fdata["clue"],
        solution=fdata["solution"],
        solution_hint=fdata["solution_hint"],
        solution_type_id=fdata["solution_type_id"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    cs.save()
    session["setter_id"] = fdata["crossword_setter_id"]
    log = (
        f"crossword_setter_id: {fdata['crossword_setter_id']}\n"
        f"clue: {fdata['clue']}\n"
        f"solution: {fdata['solution']}\n"
        f"solution_hint: {fdata['solution_hint']}\n"
        f"solution_type_id: {fdata['solution_type_id']}"
    )
    add_log(
        Users.get_name(current_user), "insert", "crossword_solutions", cs.rowid, log
    )
    flash(f"Saved new crossword solution, {fdata['solution']}")
    return redirect("/crossword-solutions/")


@application.route("/crossword-solutions/<int:csid>/edit", methods=["GET", "POST"])
@login_required
def crossword_solutions_edit(csid):
    """
    Edit an existing solution
    """
    if request.method == "GET":
        try:
            rs = crossword_hints.models.crossword_hints.crossword_solutions.get(
                crossword_hints.models.crossword_hints.crossword_solutions.rowid == csid
            )
        except DoesNotExist:
            flash(f"Cannot find crossword solution record for id, {csid}.")
            return redirect("/crossword-solutions")
        return render_template(
            "crossword-solutions/edit.html",
            soln=rs,
            s_types=get_solution_types(),
            setters=get_crossword_setters(),
            r=request,
            sbmt="Update crossword solution",
        )
    rc, fdata = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "crossword-solutions/edit.html",
            solution=fdata,
            s_types=get_solution_types(),
            setters=get_crossword_setters(),
            r=request,
            sbmt=request.form["submit"],
        )
    cs = crossword_hints.models.crossword_hints.crossword_solutions(
        rowid=csid,
        crossword_setter_id=fdata["crossword_setter_id"],
        clue=fdata["clue"],
        solution=fdata["solution"],
        solution_hint=fdata["solution_hint"],
        solution_type_id=fdata["solution_type_id"],
        updated_at=datetime.now(),
    )
    cs.save()
    log = (
        f"crossword_setter_id: {fdata['crossword_setter_id']}\n"
        f"clue: {fdata['clue']}\n"
        f"solution: {fdata['solution']}\n"
        f"solution_hint: {fdata['solution_hint']}\n"
        f"solution_type_id: {fdata['solution_type_id']}"
    )
    add_log(Users.get_name(current_user), "update", "crossword_solutions", csid, log)
    flash(f"Updated crossword solution, {fdata['solution']}")
    return redirect("/crossword-solutions")


@application.route("/crossword-solutions/<int:csid>/delete", methods=["GET"])
@login_required
def crossword_solutions_delete(csid):
    """ "
    Delete an existing solution
    """
    try:
        rs = crossword_hints.models.crossword_hints.crossword_solutions.get(
            crossword_hints.models.crossword_hints.crossword_solutions.rowid == csid
        )
    except DoesNotExist:
        flash(f"Cannot find solution record for id, {csid}.")
        return redirect("/crossword-solutions")
    log = (
        f"crossword_setter_id: {rs.crossword_setter_id}\n"
        f"clue: {rs.clue}\n"
        f"solution: {rs.solution}\n"
        f"solution_hint: {rs.solution_hint}\n"
        f"solution_type_id: {rs.solution_type_id}"
    )
    rs.delete_instance()
    add_log(Users.get_name(current_user), "delete", "crossword_solutions", csid, log)
    flash(f"Deleted crossword solution, {rs.solution}")
    return redirect("/crossword-solutions")
