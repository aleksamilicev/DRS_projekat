from flask import Blueprint, request, jsonify
from ...services.postServices.postServices import (
    create_post,
    get_post_by_id,
    update_post,
    delete_post,
    get_friends_posts
)
api = Blueprint('api', __name__)

# Posts routes
api.add_url_rule('/posts', view_func=create_post, methods=['POST'])
api.add_url_rule('/posts/<int:post_id>', view_func=update_post, methods=['PUT'])
api.add_url_rule('/posts/<int:post_id>', view_func=delete_post, methods=['DELETE'])
api.add_url_rule('/posts/friends', view_func=get_friends_posts, methods=['GET'])