from flask import Blueprint, request, jsonify
from ...services.adminServices.adminServices import (
    get_all_users, 
    create_user, 
    block_user, 
    unblock_user, 
    get_pending_posts, 
    approve_post, 
    reject_post )
api = Blueprint('api', __name__)

# admin routes
api.add_url_rule('/admin/users', view_func=get_all_users, methods=['GET'])
api.add_url_rule('/admin/users', view_func=create_user, methods=['POST'])
api.add_url_rule('/admin/users/<int:user_id>/block', view_func=block_user, methods=['POST'])
api.add_url_rule('/admin/users/<int:user_id>/unblock', view_func=unblock_user, methods=['POST'])
api.add_url_rule('/admin/posts/pending', view_func=get_pending_posts, methods=['GET'])
api.add_url_rule('/admin/posts/<int:post_id>/approve', view_func=approve_post, methods=['POST'])
api.add_url_rule('/admin/posts/<int:post_id>/reject', view_func=reject_post, methods=['POST'])