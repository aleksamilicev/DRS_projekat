from flask import Blueprint, request, jsonify
from ...services.userProfileServices.userProfileServices import (
    get_user_profile, 
    update_user_profile, 
    delete_user_profile )
user_profile_routes = Blueprint('user_profile', __name__)

# Users routes
user_profile_routes.add_url_rule('/users/<int:user_id>', view_func=get_user_profile, methods=['GET'])
user_profile_routes.add_url_rule('/users/<int:user_id>', view_func=update_user_profile, methods=['PUT'])
user_profile_routes.add_url_rule('/users/<int:user_id>', view_func=delete_user_profile, methods=['DELETE'])
