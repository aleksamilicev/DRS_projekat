from flask import Blueprint, request, jsonify
from ...services.postsServices.postsServices import (
    create_post,
    get_user_posts,
    update_post,
    delete_post,
    get_friends_posts,
    get_post_status,
    get_all_user_post_statuses,
    get_my_approved_posts
)
post_routes = Blueprint('post', __name__)

# Posts routes
post_routes.add_url_rule('/posts/create', view_func=create_post, methods=['POST'])
post_routes.add_url_rule('/posts', view_func=get_my_approved_posts, methods=['GET'])
post_routes.add_url_rule('/posts/<string:username>', view_func=get_user_posts, methods=['GET']) # za pregled objava korisnika(bilo kojeg)
post_routes.add_url_rule('/posts/<int:post_id>', view_func=update_post, methods=['PUT'])
post_routes.add_url_rule('/posts/<int:post_id>', view_func=delete_post, methods=['DELETE'])
#post_routes.add_url_rule('/posts/friends', view_func=get_friends_posts, methods=['GET'])

# NEW: Get status of a single post
post_routes.add_url_rule('/posts/<int:post_id>/status', view_func=get_post_status, methods=['GET'])

# NEW: Get status of all posts by current user
post_routes.add_url_rule('/posts/status', view_func=get_all_user_post_statuses, methods=['GET'])