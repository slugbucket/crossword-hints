"""
Site login
Params:
  None
Returns:
  jinja2 template render of the login form
"""
@application.route("/login", methods=['GET', 'POST'])
def crossword_login():
    try:
        if current_user.is_authenticated:
            flash('You are already logged in.')
            return redirect(request.path)
    except:
        pass

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            users.try_login(username, password)
        except ldap.INVALID_CREDENTIALS:
            flash(
                'Invalid username or password. Please try again.', 'danger')
            add_log(username, 'login', 'user', '-1', ('Failed login for %s: invalid username or password.' % username))
            return(render_template('views/login/login.html', u=username, r=request))
        except ldap.SERVER_DOWN:
            flash(
                'Cannot contact LDAP server, login not possible.', 'danger')
            return(render_template('views/login/login.html', u=username, r=request))

        user = users.get(users.username == username)
        try:
            login_user(user)
            add_log(username, 'login', 'user', user.get_id(), ("Successful login for %s" % username))
        except Exception as e:
            add_log(username, 'login', 'user', user.get_id(), str(e))
        return redirect_back('crossowrd_hints_index')
    else:
        username = 'username'

    return(render_template('views/login/login.html', u=username, r=request))

# somewhere to logout
@application.route("/logout")
@login_required
def logout():
    u = users.get_name(current_user)
    add_log(u, 'logout', 'user', users.get_id(current_user), ("Successful logout for %s" % u))
    logout_user()
    flash("%s logout successful. Please close browser for best security." % u)
    return(redirect("/"))

