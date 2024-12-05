from flask import Blueprint, request, jsonify
from ...services.postsServices.postsServices import (
    create_post,
    get_post_by_id,
    update_post,
    delete_post,
    get_friends_posts
)
post_routes = Blueprint('post', __name__)

# Posts routes
post_routes.add_url_rule('/posts', view_func=create_post, methods=['POST'])
post_routes.add_url_rule('/posts/<int:post_id>', view_func=update_post, methods=['PUT'])
post_routes.add_url_rule('/posts/<int:post_id>', view_func=delete_post, methods=['DELETE'])
post_routes.add_url_rule('/posts/friends', view_func=get_friends_posts, methods=['GET'])