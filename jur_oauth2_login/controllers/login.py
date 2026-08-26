# -*- coding: utf-8 -*-
import json
from flask import request, redirect, render_template, flash
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import requests
from oauthlib.oauth2 import WebApplicationClient
from crossword_hints import application
from crossword_hints.default_settings import GOOGLE_CLIENT_ID
from crossword_hints.views.crossword_hints import add_log
from jur_oauth2_login.models.users import Users

# flask-login
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "crossword_login"

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@login_manager.user_loader
def load_user(id):
    """
    Flask-Login helper to retrieve a user from our db
    """
    return Users.get(Users.rowid == int(id))


def get_google_provider_cfg():
    """
    Get the Google provider configuration
    """
    return requests.get(GOOGLE_DISCOVERY_URL, timeout=30).json()


@application.route("/login", methods=["GET", "POST"])
def crossword_login():
    """
    # Find out what URL to hit for Google login
    """
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)
    # return render_template("login/login.html", u=username, r=request)


@application.route("/login/callback")
def callback():
    """
    Get authorization code Google sent back to you
    """
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
# things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        timeout=30,
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body, timeout=30)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = Users.get_or_create(
        username=users_email,
        defaults={"created_at": None, "updated_at": None},
    )[0]

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect("/")

# somewhere to logout
@application.route("/logout")
@login_required
def logout():
    u = Users.get_name(current_user)
    add_log(
        u,
        "logout",
        "user",
        Users.get_id(current_user),
        ("Successful logout for %s" % u),
    )
    logout_user()
    flash("%s logout successful. Please close browser for best security." % u)
    return redirect("/")
