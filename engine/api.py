# /engine/api.py

from flask import Blueprint, request, jsonify

# Kreiranje Blueprint-a za API
api = Blueprint('api', __name__)

# *** AUTENTIFIKACIJA ***
@api.route('/auth/register', methods=['POST'])
def register():
    return jsonify({"message": "User registered successfully!"}), 201

@api.route('/auth/login', methods=['POST'])
def login():
    return jsonify({"message": "Login successful!", "token": "example_token"}), 200

@api.route('/auth/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout successful!"}), 200


# *** PRIJATELJI ***
@api.route('/friends/<int:user_id>/request', methods=['POST'])
def send_friend_request(user_id):
    return jsonify({"message": f"Friend request sent to user {user_id}!"}), 201

@api.route('/friends/requests', methods=['GET'])
def get_friend_requests():
    return jsonify({"message": "List of friend requests"}), 200

@api.route('/friends/<int:request_id>/accept', methods=['POST'])
def accept_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} accepted!"}), 200

@api.route('/friends/<int:request_id>/reject', methods=['POST'])
def reject_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} rejected!"}), 200

@api.route('/friends', methods=['GET'])
def get_friends():
    return jsonify({"message": "List of friends"}), 200

@api.route('/friends/<int:friend_id>', methods=['DELETE'])
def delete_friend(friend_id):
    return jsonify({"message": f"Friend {friend_id} deleted!"}), 200


# *** PRETRAGA ***
@api.route('/search/users', methods=['GET'])
def search_users():
    # Simulacija pretrage sa query parametrima
    email = request.args.get('email')
    username = request.args.get('username')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    city = request.args.get('city')
    
    query_params = {
        "email": email,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "city": city
    }
    return jsonify({"message": "Search results", "query": query_params}), 200
