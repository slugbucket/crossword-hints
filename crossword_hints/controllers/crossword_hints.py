# -*- coding: utf-8 -*-
"""
C  R  O  S  S  W  O  R  D      H  I  N  T  S
"""

from flask import request, flash, render_template
from peewee import JOIN, fn
from crossword_hints.models.crossword_hints import (
    crossword_setters,
    solution_types,
    crossword_solutions,
)
from crossword_hints import application, sanitize_input

# from crossword_hints.views.crossword_hints import *


@application.route("/crossword-hints/heartbeat", methods=["GET"])
def heartbeat():
    """
    Healthcheck
    """
    return "OK"


@application.route("/crossword-hints/", methods=["GET", "POST"], defaults={"path": ""})
@application.route("/", methods=["GET", "POST"], defaults={"path": ""})
def crossword_hints_index():
    """
    Crossword hints index
    """
    if request.method == "GET":
        return render_template("crossword-hints/index.html", r=request)
    rc, fdata = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template(
            "crossword-hints/index.html", r=request, sbmt=request.form["submit"]
        )

    clueset = (
        crossword_setters.select(
            crossword_solutions.rowid.alias("csid"),
            crossword_solutions.solution,
            crossword_solutions.clue,
            crossword_solutions.solution_hint.alias("hint"),
            solution_types.name.alias("soltype"),
            solution_types.description.alias("soltypedesc"),
            crossword_setters.name.alias("setter"),
        )
        .join(
            crossword_solutions,
            JOIN.INNER,
            on=(crossword_setters.rowid == crossword_solutions.crossword_setter),
        )
        .join(
            solution_types,
            JOIN.INNER,
            on=(crossword_solutions.solution_type == solution_types.rowid),
        )
        .where(crossword_solutions.clue.contains(format(fdata["cue_word"])))
        .order_by(fn.Lower(crossword_solutions.solution))
        .dicts()
    )
    return render_template(
        "crossword-hints/index.html",
        r=request,
        clues=clueset,
        cue_word=format(fdata["cue_word"]),
    )
