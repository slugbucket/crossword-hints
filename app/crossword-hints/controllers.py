"""                                                   """
"""   C  R  O  S  S  W  O  R  D      H  I  N  T  S    """
"""                                                   """
@application.route('/crossword-hints/heartbeat', methods=["GET"])
def heartbeat():
    return "OK"


@application.route("/crossword-hints/", methods=["GET", "POST"], defaults={'path': ''})
@application.route('/', methods=["GET", "POST"], defaults={'path': ''})
def crossowrd_hints_index(path):
    if request.method == "GET":
        return(render_template('views/crossword-hints/index.html', r=request))
    (rc, fdata) = sanitize_input(request.form)
    if not rc == "":
        flash(rc)
        return(render_template('views/crossword-hints/index.html', r=request, sbmt=request.form['submit']))

    clueset = crossword_setters.select(crossword_solutions.rowid.alias("csid"),
                           crossword_solutions.solution,
                           crossword_solutions.clue,
                           crossword_solutions.solution_hint.alias("hint"),
                           solution_types.name.alias("soltype"),
                           crossword_setters.name.alias("setter")) \
                          .join(crossword_solutions, JOIN.INNER, on=(crossword_setters.rowid == crossword_solutions.crossword_setter_id)) \
                          .join(solution_types, JOIN.INNER, on=(crossword_solutions.solution_type_id == solution_types.rowid)) \
                          .where(crossword_solutions.clue.contains(format(fdata['cue_word']))) \
                          .order_by(fn.Lower(crossword_solutions.solution)).dicts()
    return(render_template('views/crossword-hints/index.html', r=request, clues=clueset))
