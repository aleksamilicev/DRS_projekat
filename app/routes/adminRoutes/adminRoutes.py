from flask import Blueprint, request, jsonify
from ...services.adminServices.adminServices import (
    get_all_users, 
    get_all_blocked_users,
    create_user, 
    block_user, 
    unblock_user, 
    get_pending_posts, 
    approve_post,
    accept_registration,
    reject_registration,
    reject_post,
    get_pending_registrations
    )
admin_routes = Blueprint('admin', __name__)

# admin routes
admin_routes.add_url_rule('/admin/users', view_func=get_all_users, methods=['GET'])
admin_routes.add_url_rule('/admin/users/blocked', view_func=get_all_blocked_users, methods=['GET'])
# admin_routes.add_url_rule('/admin/users', view_func=create_user, methods=['POST'])
admin_routes.add_url_rule('/admin/users/<int:user_id>/block', view_func=block_user, methods=['POST'])
admin_routes.add_url_rule('/admin/users/<int:user_id>/unblock', view_func=unblock_user, methods=['POST'])
admin_routes.add_url_rule('/admin/posts/pending', view_func=get_pending_posts, methods=['GET'])
admin_routes.add_url_rule('/admin/posts/<int:post_id>/approve', view_func=approve_post, methods=['POST'])
admin_routes.add_url_rule('/admin/posts/<int:post_id>/reject', view_func=reject_post, methods=['POST'])

admin_routes.add_url_rule('/admin/registration/<int:user_id>/pending', view_func=get_pending_registrations, methods=['GET'])
admin_routes.add_url_rule('/admin/registration/<int:user_id>/accept', view_func=accept_registration, methods=['POST'])
admin_routes.add_url_rule('/admin/registration/<int:user_id>/reject', view_func=reject_registration, methods=['POST'])