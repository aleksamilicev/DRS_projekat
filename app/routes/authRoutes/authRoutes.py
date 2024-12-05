from flask import Blueprint, request, jsonify
from ...services.authServices.authServices import (
    register, 
    login,
    logout )
auth_routes = Blueprint('auth', __name__)

# auth routes
auth_routes.add_url_rule('/auth/register', view_func=register, methods=['POST'])
auth_routes.add_url_rule('/auth/login', view_func=login, methods=['POST'])
auth_routes.add_url_rule('/auth/logout', view_func=logout, methods=['POST'])
# front deo radi logout, samo obrise json token, uradicu to ovded za svaki slucaj