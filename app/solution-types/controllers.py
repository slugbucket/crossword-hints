"""
Route for direct rendering of the solution-types table in response to an AJAX request
"""
@application.route("/solution-types/index.ajax.html", methods=["GET"])
def solution_types_index_ajax():
    rs = solution_types.select().order_by(fn.Lower(solution_types.name))
    return render_template('views/solution-types/_index.ajax.html', stypes=rs.dicts())

"""
Solution types JSON route for AJAX requests
"""
@application.route("/solution-types/index.json", methods=["GET"])
def solution_types_index_json():
    rs = solution_types.select().order_by(fn.Lower(solution_types.name)).dicts()
    if not rs:
        return(Response('{"result": "error"}', mimetype="text/json", status_code=400))
    res = []
    for row in rs:
        res.append(dict(row))
    return(jsonify(res))

"""
Render a template of the detail of a spefic solution type
"""
@application.route("/solution-types/<int:id>", methods=["GET"])
def solution_types_show(id):
    rs = solution_types.get(solution_types.rowid == id)
    return render_template('views/solution-types/show.html', stype=rs,  r=request)

"""
Display a form requesting the details of a new solution type
"""
@application.route("/solution-types/new", methods=["GET", "POST"])
@login_required
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
    log = ("name: %s\ndescription: %s" % (fdata['name'], fdata['description']))
    add_log(users.get_name(current_user), 'insert', 'solution_types', st.rowid, log)
    flash("Saved new solution type, %s" % fdata['name'])
    return redirect('/solution-types')

"""
Display a form to edit the details of an existing solution type
"""
@application.route("/solution-types/<int:id>/edit", methods=["GET", "POST"])
@login_required
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
    log = ("name: %s\ndescription: %s" % (fdata['name'], fdata['description']))
    add_log(users.get_name(current_user), 'update', 'solution_types', id, log)
    flash("Updated solution type, %s" % fdata['name'])
    return(redirect('/solution-types'))

"""
Delete an existing solution type
"""
@application.route("/solution-types/<int:id>/delete", methods=["GET", "POST"])
@login_required
def solution_types_delete(id):
    try:
        rs = solution_types.get(solution_types.rowid == id)
    except DoesNotExist:
        flash("Cannot find solution type record for id, %s." % id)
        return(redirect('/solution-types'))
    log = ("name: %s\ndescription: %s" % (rs.name, rs.description))
    rs.delete_instance()
    add_log(users.get_name(current_user), 'delete', 'solution_types', rs.rowid, log)
    flash("Deleted solution type, %s" % rs.name)
    return(redirect("/solution-types"))
