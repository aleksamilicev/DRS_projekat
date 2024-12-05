from flask import Blueprint, request, jsonify
from ...services.friendsServices.friendsServices import (
    send_friend_request, 
    get_friend_requests,
    accept_friend_request,
    reject_friend_request,
    get_friends,
    delete_friend )
friends_routes = Blueprint('friends', __name__)

friends_routes.add_url_rule('/friends/<int:user_id>/request', view_func=send_friend_request, methods=['POST'])
friends_routes.add_url_rule('/friends/requests', view_func=get_friend_requests, methods=['GET'])
friends_routes.add_url_rule('/friends/<int:request_id>/accept', view_func=accept_friend_request, methods=['POST'])
friends_routes.add_url_rule('/friends/<int:request_id>/reject', view_func=reject_friend_request, methods=['POST'])
friends_routes.add_url_rule('/friends', view_func=get_friends, methods=['GET'])
friends_routes.add_url_rule('/friends/<int:friend_id>', view_func=delete_friend, methods=['DELETE'])