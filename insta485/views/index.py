"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import redirect, render_template
from flask import session, abort, send_from_directory
import arrow
from insta485.model import query_db
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if "user" not in session:
        return redirect("/accounts/login/")

    # Query database
    posts = query_db(
        "SELECT DISTINCT posts.postid, posts.filename, "
        "posts.created, posts.owner "
        "FROM posts INNER JOIN following ON "
        "(posts.owner = following.username2 AND following.username1 =?) "
        "OR (posts.owner =?)"
        "ORDER BY posts.postid DESC", (session["user"], session["user"])
    )

    for pst in posts:
        pic = query_db(
            "SELECT filename FROM users "
            "WHERE "
            "username = ? ", (pst["owner"],), True
        )
        pst["profile_picture"] = pic["filename"]

        arrow.get(pst["created"])
        pst["humanize"] = arrow.utcnow().humanize()
        pst["likes"] = query_db(
            "SELECT COUNT(*) FROM likes "
            "WHERE postid=? ", (pst["postid"],), True
        )["COUNT(*)"]
        pst["like_login"] = bool(query_db(
            "SELECT * FROM likes "
            "WHERE owner = ? AND postid=?", (session["user"], pst["postid"])
        ))
        pst["comments"] = query_db(
            "SELECT text AS comment, owner, "
            "text, postid FROM comments "
            "WHERE postid=? ORDER BY commentid ASC", (pst["postid"],)
        )
    # Add database info to context
    context = {"posts": posts, "logname": session["user"]}
    return flask.render_template("index.html", **context)


@insta485.app.route('/p/<postid_url_slug>/')
def post(postid_url_slug):
    """Post."""
    if "user" not in session:
        return redirect("/accounts/login/")

    # Query database
    post1 = query_db(
        "SELECT posts.postid, posts.filename, posts.created, posts.owner "
        "FROM posts "
        "WHERE posts.postid = ?", (postid_url_slug)
    )
    post1 = post1[0]

    arrow.get(post1["created"])
    humanize = arrow.utcnow().humanize()
    post1["humanize"] = humanize

    likes = query_db(
        "SELECT COUNT (likes.owner) FROM likes "
        "WHERE postid = ?", (postid_url_slug)
    )
    post1["likes"] = likes[0]["COUNT (likes.owner)"]

    like_login = query_db(
        "SELECT postid FROM likes "
        "WHERE owner = ? AND postid = ?", (session["user"], postid_url_slug)
    )
    if len(like_login) > 0:
        post1["like_login"] = True
    else:
        post1["like_login"] = False

    comments = query_db(
        "SELECT comments.commentid, comments.owner, "
        "comments.text, comments.postid FROM comments "
        "WHERE comments.postid = ? "
        "ORDER BY commentid", (postid_url_slug)
    )

    post1["comments"] = []
    for comment in comments:
        data = {"comment": comment["text"],
                "owner": comment["owner"],
                "commentid": comment["commentid"]}
        post1["comments"].append(data)

    profile_picture = query_db(
        "SELECT filename FROM users "
        "WHERE username = ?", (post1["owner"],)
    )
    # Add database info to context
    context = {"post": post1}
    context["logname"] = session["user"]
    context["profile_picture"] = profile_picture[0]["filename"]
    return flask.render_template("post.html", **context)


@insta485.app.route('/explore/')
def explore():
    """Explore."""
    if "user" not in session:
        return redirect("/accounts/login/")
    # Query database
    users = query_db(
        "SELECT username, filename "
        "FROM users WHERE username NOT IN "
        "( SELECT username2 FROM following WHERE "
        "username1 = ?)", (session["user"],)
    )
    # for i in range(len(users)):
    #     if users[i]['username'] == session["user"]:
    #         del users[i]
    #         break

    users = [user1 for user1 in users if user1['username'] != session["user"]]

    context = {"users": users}
    context["logname"] = session["user"]
    return render_template("explore.html", **context)


@insta485.app.route('/u/<user_url_slug>/')
def user(user_url_slug):
    """User page."""
    if "user" not in session:
        return redirect("/accounts/login/")

    # Query database
    users = query_db(
        "SELECT username "
        "FROM users WHERE username = ? ", (user_url_slug,)
    )
    if len(users) == 0:
        abort(404)

    user1 = users[0]
    context = {"user": user1}

    context["following"] = ""
    if "user" in session:
        check = False
        following1 = query_db(
            "SELECT username2 "
            "FROM following WHERE username1 = ? ", (session["user"],)
        )
        if session["user"] != user_url_slug:
            for i in following1:
                if i["username2"] == user_url_slug:
                    context["following"] = "following"
                    check = True

            if not check:
                context["following"] = "not following"

        else:
            context["following"] = "myself"

    posts = query_db(
        "SELECT postid "
        "FROM posts WHERE owner = ? ", (user_url_slug,)
    )

    context["posts_num"] = len(posts)

    followers1 = query_db(
        "SELECT username1 "
        "FROM following WHERE username2 = ? ", (user_url_slug,)
    )

    context["followers_num"] = len(followers1)
    context["followers"] = followers1

    following1 = query_db(
        "SELECT username2 "
        "FROM following WHERE username1 = ? ", (user_url_slug,)
    )

    context["following_num"] = len(following1)

    names = query_db(
        "SELECT fullname "
        "FROM users WHERE username = ? ", (user_url_slug,)
    )

    name = names[0]
    context["name"] = name

    pictures = query_db(
        "SELECT filename "
        "FROM posts WHERE owner = ? ", (user_url_slug,)
    )
    context["pictures"] = pictures

    posts_context = []
    for i, pst in enumerate(posts):
        posts_context.append(
            {"postid": pst["postid"], "url": pictures[i]["filename"]})

    context["posts_context"] = posts_context
    context["logname"] = session["user"]

    return render_template("user.html", **context)


@insta485.app.route('/u/<user_url_slug>/following/')
def following(user_url_slug):
    """Following."""
    if "user" not in session:
        return redirect("/accounts/login/")

    users = query_db(
        "SELECT username "
        "FROM users WHERE username = ? ", (user_url_slug,)
    )

    if len(users) == 0:
        abort(404)

    context = {}
    ret = []
    following1 = query_db(
        "SELECT username2 "
        "FROM following WHERE username1 = ? ", (user_url_slug,)
    )

    for following_user in following1:
        icon = query_db(
            "SELECT filename "
            "FROM users WHERE username = ? ", (following_user["username2"],)
        )
        icon_real = icon[0].get("filename")

        login_following = query_db(
            "SELECT username2 "
            "FROM following WHERE username1 = ? AND username2 = ?", (
                session["user"], following_user["username2"],)
        )

        if session["user"] != following_user["username2"]:
            if len(login_following) > 0:
                ret.append({"icon": icon_real,
                            "username": following_user["username2"],
                            "login_following": "following"})
            else:
                ret.append({"icon": icon_real,
                            "username": following_user["username2"],
                            "login_following": "not following"})
        else:
            ret.append({"icon": icon_real,
                        "username": following_user["username2"],
                        "login_following": "myself"})

    context["ret"] = ret

    context["current"] = user_url_slug
    context["logname"] = session["user"]
    return render_template("following.html", **context)


@insta485.app.route('/u/<user_url_slug>/followers/')
def followers(user_url_slug):
    """Followers."""
    if "user" not in session:
        return redirect("/accounts/login/")

    users = query_db(
        "SELECT username "
        "FROM users WHERE username = ? ", (user_url_slug,)
    )

    if len(users) == 0:
        abort(404)

    context = {}
    ret = []

    following1 = query_db(
        "SELECT username1 "
        "FROM following WHERE username2 = ? ", (user_url_slug,)
    )

    for following_user in following1:
        icon = query_db(
            "SELECT filename "
            "FROM users WHERE username = ? ", (following_user["username1"],)
        )
        icon_real = icon[0].get("filename")

        login_following = query_db(
            "SELECT username2 "
            "FROM following WHERE username1 = ? AND username2 = ?", (
                session["user"], following_user["username1"],)
        )

        if session["user"] != following_user["username1"]:
            if len(login_following) > 0:
                ret.append({"icon": icon_real,
                            "username": following_user["username1"],
                            "login_following": "following"})
            else:
                ret.append(
                    {"icon": icon_real,
                     "username": following_user["username1"],
                     "login_following": "not following"})
        else:
            ret.append({"icon": icon_real,
                        "username": following_user["username1"],
                        "login_following": "myself"})

    context["ret"] = ret
    context["current"] = user_url_slug
    context["logname"] = session["user"]
    return render_template("followers.html", **context)


@insta485.app.route("/uploads/<image_name>")
def get_image(image_name):
    """Get image."""
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory(
            insta485.app.config["UPLOAD_FOLDER"],
            filename=image_name, as_attachment=False
        )
    except FileNotFoundError:
        abort(404)
