from flask import Blueprint, request, jsonify
from ...services.postsServices.postsServices import (
    create_post,
    get_user_posts,
    update_post,
    delete_post,
    get_friends_posts
)
post_routes = Blueprint('post', __name__)

# Posts routes
post_routes.add_url_rule('/posts/create', view_func=create_post, methods=['POST'])
post_routes.add_url_rule('/posts/<int:user_id>', view_func=get_user_posts, methods=['GET']) # za pregled objava korisnika(bilo kojeg)
post_routes.add_url_rule('/posts/<int:post_id>', view_func=update_post, methods=['PUT'])
post_routes.add_url_rule('/posts/<int:post_id>', view_func=delete_post, methods=['DELETE'])
post_routes.add_url_rule('/posts/friends', view_func=get_friends_posts, methods=['GET'])