from flask import jsonify, request, current_app

def send_friend_request(user_id):
    return jsonify({"message": f"Friend request sent to user {user_id}!"}), 201

def get_friend_requests():
    return jsonify({"message": "List of friend requests"}), 200

def accept_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} accepted!"}), 200

def reject_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} rejected!"}), 200

def get_friends():
    return jsonify({"message": "List of friends"}), 200

def delete_friend(friend_id):
    return jsonify({"message": f"Friend {friend_id} deleted!"}), 200