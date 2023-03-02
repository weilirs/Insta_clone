"""Insta485 post requests for data manipulation."""
import uuid
import hashlib
from flask import redirect, url_for, request, session, abort
from insta485.model import query_db
import insta485
from insta485.image import save_img, del_img


def gen_password(password):
    """Generate password hash for db storage."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def verify_password(password, hashed):
    """Verify entered password against hashed password."""
    parsed = hashed.split("$")
    hash_obj = hashlib.new(parsed[0])
    password_salted = parsed[1] + password
    hash_obj.update(password_salted.encode('utf-8'))
    return parsed[2] == hash_obj.hexdigest()


@insta485.app.route("/likes/", methods=["POST"])
def like_post():
    """Handle liking and unliking posts."""
    url = request.args.get('target')
    operation = request.form["operation"]
    if "user" not in session:
        abort(403)
    res = query_db("SELECT * FROM likes WHERE owner = ? AND postid = ?",
                   (session["user"], request.form["postid"]))
    if operation == "like":
        if res:
            abort(409)
        query_db("INSERT INTO likes (owner, postid) VALUES(?, ?) ",
                 (session["user"], request.form["postid"]))
    elif operation == "unlike":
        if not res:
            abort(409)
        query_db("DELETE FROM likes WHERE owner=? AND postid=?",
                 (session["user"], request.form["postid"]))
    return redirect(url if url else "/")


@insta485.app.route("/comments/", methods=["POST"])
def comment_post():
    """Handle creating and deleting comments."""
    url = request.args.get('target')
    operation = request.form["operation"]
    if operation == "create":
        # check logged in
        if "user" not in session:
            abort(403)

        # check for text
        if not request.form["text"]:
            abort(400)

        # insert comment into db
        query_db(
            "INSERT INTO comments (postid, text, owner) VALUES(?, ?, ?) ",
            (request.form["postid"], request.form["text"], session["user"]))
    elif operation == "delete":
        # check ownership
        query = "SELECT owner FROM comments WHERE commentid=?"
        if "user" not in session or session["user"] != \
                query_db(query, (request.form["commentid"],), True)["owner"]:
            abort(403)

        # delete db entry
        query_db("DELETE FROM comments WHERE commentid=?",
                 (request.form["commentid"],))
    return redirect(url if url else "/")


@insta485.app.route("/posts/", methods=["POST"])
def post_post():
    """Handle creating and deleting posts."""
    url = request.args.get('target')
    operation = request.form["operation"]
    if operation == "create":
        # check logged in
        if "user" not in session:
            abort(403)

        # check for file
        if not request.files["file"]:
            abort(400)

        # insert post into db
        query_db("INSERT INTO posts (filename, owner) "
                 "VALUES(?, ?) ", (save_img(request.files["file"]),
                                   session["user"]))
    elif operation == "delete":
        res = query_db("SELECT owner, filename FROM posts WHERE postid=?",
                       (request.form["postid"],), True)
        # check ownership
        if "user" not in session or session["user"] != res["owner"]:
            abort(403)

        # delete iamge
        del_img(res["filename"])

        # delete db entry
        query_db("DELETE FROM posts WHERE postid=?", (request.form["postid"],))
    return redirect(url if url else
                    url_for("user", user_url_slug=session["user"]))


@insta485.app.route("/following/", methods=["POST"])
def follow_post():
    """Handle following and unfollowing people."""
    url = request.args.get('target')

    operation = request.form["operation"]

    name = request.form["username"]

    # authentication
    connection = insta485.model.get_db()

    if operation == "follow":
        # check duplicate
        check = connection.execute(
            "SELECT username1 FROM following "
            "WHERE username1 = ? AND username2 = ?", (session["user"], name)
        )
        checked = check.fetchall()
        if checked:
            abort(409)

        # update database
        connection.execute(
            "INSERT INTO following (username1, username2) "
            "VALUES (?, ?)", (session["user"], name)
        )

    elif operation == "unfollow":
        # check duplicate
        check = connection.execute(
            "SELECT username1 FROM following "
            "WHERE username1 = ? AND username2 = ?", (session["user"], name)
        )
        checked = check.fetchall()
        if not checked:
            abort(409)

        # update database
        connection.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ?", (session["user"], name)
        )
    return redirect(url if url else "/")


def handle_login():
    """Handle account login."""
    username = request.form["username"]
    password = request.form["password"]

    # check field not empty
    if not username or not password:
        abort(400)

    # check field valid
    res = query_db(
        "SELECT password FROM users WHERE username=?", (username,), True)
    if not res or not verify_password(password, res["password"]):
        abort(403)

    # log in the user
    session["user"] = username


def handle_create():
    """Handle account creation."""
    file_obj = request.files["file"]
    fullname = request.form["fullname"]
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    # check field not empty
    if not (file_obj and fullname and username and email and password):
        abort(400)

    # user already exists
    if query_db("SELECT * FROM users WHERE username=?", (username,)):
        abort(409)

    uuid_basename = save_img(file_obj)

    # add user to database
    query_db(
        "INSERT INTO users (username,fullname,email,filename,password) "
        "VALUES(?,?,?,?,?) ", (username, fullname, email,
                               uuid_basename, gen_password(password))
    )

    # log in the user
    session["user"] = username


def handle_delete():
    """Handle account deletion."""
    # check if user is logged in
    if "user" not in session:
        abort(403)

    # delete pictures from posts
    posts = query_db("SELECT filename FROM posts WHERE owner=?",
                     (session["user"],))
    for post in posts:
        del_img(post["filename"])

    # delete profile pic
    del_img(query_db("SELECT filename FROM users WHERE username=?",
                     (session["user"],), True)["filename"])

    # delete user
    query_db(
        "DELETE FROM users WHERE username=?", (session["user"],)
    )

    session.clear()


@insta485.app.route("/accounts/", methods=["POST"])
def account_post():
    """Handle account manipulation."""
    url = request.args.get('target')
    operation = request.form["operation"]

    if operation == "login":
        handle_login()
    elif operation == "create":
        handle_create()
    elif operation == "delete":
        handle_delete()
    elif operation == "edit_account":
        # check if user is logged in
        if "user" not in session:
            abort(403)
        file_obj = request.files["file"] if "file" in request.files else None
        fullname = request.form["fullname"]
        email = request.form["email"]

        # update details
        query_db(
            "UPDATE users "
            "SET fullname=?, email=? "
            "WHERE username=?", (fullname, email, session["user"]))

        if file_obj:
            # delete previous profile pic
            del_img(query_db(
                "SELECT filename FROM users "
                "WHERE username=?", (session["user"],), True)["filename"])
            uuid_basename = save_img(file_obj)

            # update profile pic
            query_db(
                "UPDATE users "
                "SET filename=? "
                "WHERE username=?", (uuid_basename, session["user"]))

    elif operation == "update_password":
        # check if user is logged in
        if "user" not in session:
            abort(403)

        password = request.form["password"]
        new_password1 = request.form["new_password1"]
        new_password2 = request.form["new_password2"]

        # check field not empty
        if not password or not new_password1 or not new_password2:
            abort(400)

        # check password correctness
        if query_db("SELECT username, password FROM users "
                    "WHERE username=? AND password=?",
                    (session["user"], gen_password(password))):
            abort(403)

        # check password1=password2
        if new_password1 != new_password2:
            abort(401)

        # update password in db
        query_db("UPDATE users SET password=? WHERE username=?",
                 (gen_password(new_password1), session["user"]))
    return redirect(url if url else "/")
