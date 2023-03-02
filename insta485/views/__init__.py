"""Views, one for each Insta485 page."""
from insta485.views.index import show_index, explore
from insta485.views.index import followers, following, get_image, user

from insta485.views.accounts import login, logout, create
from insta485.views.accounts import delete, edit, password

from insta485.views.post import post_post, account_post, like_post
from insta485.views.post import follow_post, comment_post, gen_password
