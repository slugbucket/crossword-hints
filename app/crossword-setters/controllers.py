"""
Index listing of known setters
"""
@application.route("/crossword-setters/", methods=["GET"], defaults={'page': 1})
@application.route('/crossword-setters/page/<int:page>')
def crossword_setters_index(page):
    count = crossword_setters.select(fn.COUNT(crossword_setters.rowid)).scalar()
    offset = ((int(page)-1) * application.config['PER_PAGE'])
    rs = crossword_setters.select(crossword_setters.rowid, crossword_setters.name, crossword_setters.description, setter_types.name.alias('setter_type_name')).join(setter_types).where(crossword_setters.setter_type_id == setter_types.rowid).limit(application.config['PER_PAGE']).offset(offset).order_by(fn.Lower(crossword_setters.name))
    if not rs and page != 1:
        return(render_template('errors/409.html', errmsg="Requested page out of bounds"), 409 )
    return render_template('views/crossword-setters/index.html',
                           setters=rs.dicts(),
                           pagination=Pagination(page, application.config['PER_PAGE'], count),
                           r=request)

@application.route("/crossword-setters/<int:id>", methods=["GET"])
def crossword_setters_show(id):
    # Getting the setter id, name and setter_type name should be a simple inner
    # join across the tables but Peewee makes a complete mess of it by using get() which doesn't
    # seem to recognise aliases or joins.
    rs = crossword_setters.select(crossword_setters.rowid,
                            crossword_setters.name,
                            crossword_setters.description,
                            setter_types.name.alias('setter_type_name')) \
                        .join(setter_types, JOIN.INNER, on=(crossword_setters.setter_type_id == setter_types.rowid)) \
                        .where(crossword_setters.rowid == id).tuples()
    for id, sname, descrip, stname in rs:
        setter = {"rowid": id, "name": sname, "description": descrip, "setter_type_name": stname}
    return render_template('views/crossword-setters/show.html', setter=setter,  r=request)

"""
Add a new crossword setter
"""
@application.route("/crossword-setters/new", methods=["GET", "POST"])
@login_required
def crossword_setters_new():
    if request.method == "GET":
        setter={'name': "New setter", 'setter_type_id': 1}
        return render_template('views/crossword-setters/new.html', setter=setter, s_types=get_setter_types(), r=request, sbmt='Save new crossword setter')
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/crossword-setters/new.html', setter=fdata, s_types=get_setter_types(), r=request, sbmt=request.form['submit']))
    cs = crossword_setters(name=fdata['name'], setter_type_id=fdata['setter_type_id'], description=fdata['description'])
    cs.save()
    log = ("name: %s\nsetter_type_id: %s\ndescription: %s" %
          (fdata['name'], fdata['setter_type_id'], fdata['description']))
    add_log(users.get_name(current_user), 'insert', 'crossword_setters', cs.rowid, log)
    flash("Saved new crossword setter, %s" % fdata['name'])
    return redirect('/crossword-setters/')

"""
Edit an existing setter
"""
@application.route("/crossword-setters/<int:id>/edit", methods=["GET", "POST"])
@login_required
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
    log = ("name: %s\nsetter_type_id: %s\ndescription: %s" %
          (fdata['name'], fdata['setter_type_id'], fdata['description']))
    add_log(users.get_name(current_user), 'update', 'crossword_setters', id, log)
    flash("Updated crossword setter, %s" % fdata['name'])
    return(redirect('/crossword-setters'))

"""
Delete an existing setter
"""
@application.route("/crossword-setters/<int:id>/delete", methods=["GET"])
@login_required
def crossword_setters_delete(id):
    try:
        rs = crossword_setters.get(crossword_setters.rowid == id)
    except DoesNotExist:
        flash("Cannot find crssword setter record for id, %s." % id)
        return(redirect('/crossword-setters/'))
    log = ("name: %s\nsetter_type_id: %s\ndescription: %s" %
          (rs.name, rs.setter_type_id, rs.description))
    rs.delete_instance()
    add_log(users.get_name(current_user), 'delete', 'crossword_setters', id, log)
    flash("Deleted crossword setter, %s" % rs.name)
    return(redirect('/crossword-setters/'))
