from flask import Blueprint, request, jsonify
from ...services.searchServices.searchServices import (
    search_users )
search_routes = Blueprint('search', __name__)

# search routes
search_routes.add_url_rule('/search/users', view_func=search_users, methods=['GET'])