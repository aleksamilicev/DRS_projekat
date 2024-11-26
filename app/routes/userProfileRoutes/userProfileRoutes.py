from flask import Blueprint, request, jsonify
from ...services.userProfileServices.userProfileServices import (
    get_user_profile, 
    update_user_profile, 
    delete_user_profile )
api = Blueprint('api', __name__)

# Users routes
api.add_url_rule('/users/<int:user_id>', view_func=get_user_profile, methods=['GET'])
api.add_url_rule('/users/<int:user_id>', view_func=update_user_profile, methods=['PUT'])
api.add_url_rule('/users/<int:user_id>', view_func=delete_user_profile, methods=['DELETE'])
