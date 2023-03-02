"""REST API for posts."""
import flask
from flask import request
from flask import session, abort
from insta485.model import query_db
import insta485


@insta485.app.route('/api/v1/', methods=["GET"])
def get_services():
    """Return list of services."""
    serv = {
        "posts": "/api/v1/p/",
        "url": "/api/v1/"
    }
    return serv


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_posts():
    """Return 10 newest posts."""
    if "user" not in session:
        abort(403)

    size = request.args.get("size", default=2, type=int)
    page = request.args.get("page", default=0, type=int)
    postid_lte = request.args.get("postid_lte",default=100,type=int)
    page_index = page * size

    if size < 0 or page < 0:
        return {"message": "Bad Request", "status_code": 400}

    posts = query_db(
        "SELECT posts.postid "
        "FROM posts "
        "WHERE posts.postid <= ? AND (posts.owner IN (SELECT username2 "
        "FROM following WHERE username1 = ?) "
        "OR posts.owner = ?)"
        "ORDER BY postid DESC "
        "LIMIT ? OFFSET ?",
        (postid_lte,session["user"], session["user"], size, page_index,)
    )

    for post in posts:
        post['url'] = flask.request.path + str(post['postid']) + '/'

    next_page = ""
    if size <= len(posts):
        next_page = flask.request.path + "?size="
        next_page = next_page + str(size) + "&page=" + str(page + 1)

    context = {"next": next_page, "results": posts, "url": '/api/v1/p/',"size":size,"page":page}

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post(postid_url_slug):
    """Return post on postid."""
    if "user" not in session:
        abort(403)

    post = query_db(
        "SELECT posts.created, posts.filename, posts.owner "
        "FROM posts "
        "WHERE posts.postid = ?", (postid_url_slug,)
    )
    if post:
        context = post[0]
    else:
        return {}

    context['img_url'] = '/uploads/' + context['filename']

    user_img = query_db(
        "SELECT users.filename "
        "FROM users WHERE username = ? ", (context['owner'],)
    )

    user_img_con = user_img[0]

    context['owner_img_url'] = "/uploads/" + user_img_con['filename']
    context['owner_show_url'] = "/u/" + context['owner'] + '/'
    context['postid'] = "/p/{}/".format(postid_url_slug)
    context['url'] = flask.request.path
    context.pop('filename', None)

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<postid>/comments/', methods=["GET"])
def get_comments(postid):
    """Return comments for postid."""
    if "user" not in session:
        abort(403)

    comments = query_db(
        "SELECT comments.commentid, comments.owner, "
        "comments.text, comments.postid FROM comments "
        "WHERE comments.postid = ? "
        "ORDER BY commentid", (postid)
    )

    for comment in comments:
        comment["owner_show_url"] = "/u/" + comment["owner"] + "/"

    context = {"comments": comments}
    url = "/api/v1/p/" + postid + "/comments/"
    context["url"] = url
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<postid>/comments/', methods=["POST"])
def post_comments(postid):
    """Post a comment to postid."""
    if "user" not in session:
        abort(403)

    text = request.json
    query_db(
        "INSERT INTO comments (postid, text, owner) VALUES(?, ?, ?) ",
        (postid, text, session["user"]))

    comments = query_db(
        "SELECT comments.commentid, comments.owner, "
        "comments.text, comments.postid FROM comments "
        "WHERE comments.commentid = last_insert_rowid()"
    )

    comments[0]["owner_show_url"] = "/u/" + comments[0]["owner"] + "/"

    comment = comments[0]

    context = comment
    return flask.jsonify(context), 201


@insta485.app.route('/api/v1/p/<postid>/likes/', methods=["GET"])
def get_likes(postid):
    """Get number of likes on postid."""
    if "user" not in session:
        abort(403)

    likes = query_db(
        "SELECT owner FROM likes "
        "WHERE postid= ? "
        "UNION "
        "SELECT COUNT(*) FROM likes "
        "WHERE postid= ? ", (postid, postid,)
    )

    context = {
        "logname_likes_this": 0,
        "likes_count": likes[0]['owner'],
        "postid": int(postid),
        "url": '/api/v1/p/' + str(postid) + '/likes/'
    }
    if likes[0]['owner'] != 0:
        if session.get('user') in likes[1]['owner']:
            context['logname_likes_this'] = 1

    return flask.jsonify(context)


@insta485.app.route('/api/v1/p/<int:postid>/likes/', methods=["DELETE"])
def del_like(postid):
    """Delete session user's like from postid."""
    if "user" not in session:
        abort(403)
    query_db(
        "DELETE FROM likes "
        "WHERE postid= ? "
        "AND owner = ?", (postid, session.get('user'),)
    )
    return flask.jsonify(""), 204


@insta485.app.route('/api/v1/p/<int:postid>/likes/', methods=["POST"])
def add_like(postid):
    """Post request to add like to postid."""
    if "user" not in session:
        abort(403)

    like_exists = query_db(
        "SELECT likes.owner, likes.postid FROM likes "
        "WHERE owner = ? AND postid = ?", (session.get('user'), postid,)
    )
    if like_exists:
        context = {
            "logname": session['user'],
            "message": "Conflict",
            "postid": postid,
            "status_code": 409
        }
        return flask.jsonify(context), 409

    query_db(
        "INSERT INTO likes (owner, postid) VALUES(?, ?) ",
        (session["user"], postid,))
    context = {
        "logname": session['user'],
        "postid": postid,
    }
    return flask.jsonify(context), 201
