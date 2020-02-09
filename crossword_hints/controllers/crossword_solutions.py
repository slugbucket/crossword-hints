# -*- coding: utf-8 -*-
from crossword_hints import application
from crossword_hints.models.crossword_hints import crossword_setters, setter_types, crossword_solutions, solution_types
from jur_ldap_login.models.users import users
from jur_ldap_login.controllers.login import load_user
from flask import request, flash, redirect, render_template, session
from flask_login import login_required, current_user
from peewee import *
from crossword_hints.views.crossword_hints import *

"""
Index listing of known solutions
Params:
  None
Returns:
  jinja2 template render of list of active requests
"""
@application.route("/crossword-solutions/", defaults={'page': 1})
@application.route('/crossword-solutions/page/<int:page>')
@application.route('/crossword-solutions/search', methods=["POST"], defaults={'page': 1})
def crossword_solution_index(page):
    offset = ((int(page)-1) * application.config['PER_PAGE'])
    term = ''
    qtrm = '%'
    if request.method == "POST":
        (rc, fdata) = sanitize_input(request.form)
        term = fdata["search_box"]
        qtrm = "%" + term + "%"
    else:
        if request.args.get('q'):
            term = request.args.get('q')
            qtrm = "%" + term + "%"

    rs = crossword_setters.select(crossword_solutions.rowid.alias("csid"),
                           crossword_solutions.solution,
                           crossword_solutions.clue,
                           solution_types.name.alias("soltype"),
                           crossword_setters.name.alias("setter")) \
                          .join(crossword_solutions, JOIN.INNER, on=(crossword_setters.rowid == crossword_solutions.crossword_setter_id)) \
                          .join(solution_types, JOIN.INNER, on=(crossword_solutions.solution_type_id == solution_types.rowid)) \
                          .where(crossword_solutions.solution.contains(term) | \
                                 crossword_setters.name.contains(term) | \
                                 solution_types.name.contains(term)) \
                          .order_by(fn.Lower(crossword_solutions.solution)).dicts()
    count = len(rs)
    solutions = rs.paginate(page, application.config['PER_PAGE'])
    # Display a 409 not found page for an out of bounds request
    if not solutions and page != 1:
        return(render_template('errors/409.html', errmsg="Requested page out of bounds"), 409 )
    return render_template('crossword-solutions/index.html',
                           r=request,
                           solns=solutions,
                           pagination=Pagination(page, application.config['PER_PAGE'], count), search_term=term)

"""
Display an existing solution
"""
@application.route("/crossword-solutions/<int:id>", methods=["GET"])
def crossword_solutions_show(id):
    rs = crossword_setters.select(crossword_solutions.rowid.alias("csid"),
                           crossword_solutions.solution,
                           crossword_solutions.clue,
                           crossword_solutions.solution_hint.alias("hint"),
                           solution_types.name.alias("soltype"),
                           crossword_setters.name.alias("setter")) \
                          .join(crossword_solutions, JOIN.INNER, on=(crossword_setters.rowid == crossword_solutions.crossword_setter_id)) \
                          .join(solution_types, JOIN.INNER, on=(crossword_solutions.solution_type_id == solution_types.rowid)) \
                          .where(crossword_solutions.rowid == id) \
                          .order_by(fn.Lower(crossword_solutions.solution)).tuples()
    for  csid, solution, clue, hint, soltype, setter in rs:
        xsol = {"csid": csid, "setter": setter, "solution": solution, "clue": clue, "hint": hint, "soltype": soltype}
    return render_template('crossword-solutions/show.html', soln=xsol,  r=request)

"""
Add a new crossowrd solution
"""
@application.route("/crossword-solutions/new", methods=["GET", "POST"])
@login_required
def crossword_solutions_new():
    if request.method == "GET":
        setter_id = 1 if 'setter_id' not in session else session['setter_id']
        solution={'clue': "Clue to the answer",
                  'solution': 'Thesolution',
                  'solution_hint': 'New solution hint',
                  'crossword_setter_id': setter_id,
                  'solution_type_id': 1}
        return render_template('crossword-solutions/new.html', soln=solution, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt='Save new crossword solution')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return render_template('crossword-solutions/new.html', soln=fdata, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt=request.form['submit'])
    cs = crossword_solutions(crossword_setter_id=fdata['crossword_setter_id'],
                             clue=fdata['clue'],
                             solution=fdata['solution'],
                             solution_hint=fdata['solution_hint'],
                             solution_type_id=fdata['solution_type_id'],
                             created_at=datetime.now(),
                             updated_at=datetime.now())
    cs.save()
    session['setter_id'] = fdata['crossword_setter_id']
    log = ("crossword_setter_id: %s\nclue: %s\nsolution: %s\nsolution_hint: %s\nsolution_type_id: %s" %
          (fdata['crossword_setter_id'], fdata['clue'], fdata['solution'],
           fdata['solution_hint'], fdata['solution_type_id']))
    add_log(users.get_name(current_user), 'insert', 'crossword_solutions', cs.rowid, log)
    flash("Saved new crossword solution, %s" % fdata['solution'])
    return redirect('/crossword-solutions/')

"""
Edit an existing solution
"""
@application.route("/crossword-solutions/<int:id>/edit", methods=["GET", "POST"])
@login_required
def crossword_solutions_edit(id):
    if request.method == "GET":
        try:
            rs = crossword_solutions.get(crossword_solutions.rowid == id)
        except DoesNotExist:
            flash("Cannot find crossword solution record for id, %s." % id)
            return(redirect('/crossword-solutions'))
        return render_template('crossword-solutions/edit.html', soln=rs, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt='Update crossword solution')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('crossword-solutions/edit.html', solution=fdata, s_types=get_solution_types(), setters=get_crossword_setters(), r=request, sbmt=request.form['submit']))
    cs = crossword_solutions(rowid=id,
                             crossword_setter_id=fdata['crossword_setter_id'],
                             clue=fdata['clue'],
                             solution=fdata['solution'],
                             solution_hint=fdata['solution_hint'],
                             solution_type_id=fdata['solution_type_id'],
                             updated_at=datetime.now())
    cs.save()
    log = ("crossword_setter_id: %s\nclue: %s\nsolution: %s\nsolution_hint: %s\nsolution_type_id: %s" %
      (fdata['crossword_setter_id'], fdata['clue'], fdata['solution'],
       fdata['solution_hint'], fdata['solution_type_id']))
    add_log(users.get_name(current_user), 'update', 'crossword_solutions', id, log)
    flash("Updated crossword solution, %s" % fdata['solution'])
    return(redirect('/crossword-solutions'))

@application.route("/crossword-solutions/<int:id>/delete", methods=["GET"])
@login_required
def crossword_solutions_delete(id):
    try:
        rs = crossword_solutions.get(crossword_solutions.rowid == id)
    except DoesNotExist:
        flash("Cannot find solution record for id, %s." % id)
        return(redirect('/crossword-solutions'))
    log = ("crossword_setter_id: %s\nclue: %s\nsolution: %s\nsolution_hint: %s\nsolution_type_id: %s" %
      (rs.crossword_setter_id, rs.clue, rs.solution, rs.solution_hint, rs.solution_type_id))
    rs.delete_instance()
    add_log(users.get_name(current_user), 'delete', 'crossword_solutions', id, log)
    flash("Deleted crossword solution, %s" % rs.solution)
    return(redirect('/crossword-solutions'))
