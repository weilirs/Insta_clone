"""
Insta485 account view.

Handles pages for account manipulation
"""
from flask import redirect, render_template, session, url_for
import insta485
from insta485.model import query_db


@insta485.app.route('/accounts/login/')
def login():
    """Login page."""
    if "user" in session:
        return redirect(url_for("show_index"))
    return render_template("login.html", logname='')


@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Logout page."""
    session.clear()
    return redirect(url_for("login"))


@insta485.app.route('/accounts/create/')
def create():
    """Account creation page."""
    if "user" in session:
        return redirect(url_for("edit"))
    return render_template("create.html", logname='')


@insta485.app.route('/accounts/delete/')
def delete():
    """Account deletion page."""
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("delete.html", logname=session["user"])


@insta485.app.route('/accounts/edit/')
def edit():
    """Account edit page."""
    if "user" not in session:
        return redirect("/accounts/login/")
    res = query_db(
        "SELECT filename,fullname,email FROM users WHERE username=?",
        (session["user"],), True)
    # fix later
    img_path = "/uploads/" + res["filename"]
    context = {"logname": session["user"], "img": img_path,
               "email": res["email"], "fullname": res["fullname"]}
    return render_template("edit.html", **context)


@insta485.app.route('/accounts/password/')
def password():
    """Change password page."""
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("password.html", logname=session["user"])
