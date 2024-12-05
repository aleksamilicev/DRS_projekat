from flask import jsonify, request

# Users route functions
def get_user_profile(user_id):
    # To do
    return jsonify({"message": f"Retrieved profile for user {user_id}"}), 200

def update_user_profile(user_id):
    ## To do
    return jsonify({"message": f"Updated profile for user {user_id}"}), 200

def delete_user_profile(user_id):
    # To do
    return jsonify({"message": f"Deleted profile for user {user_id}"}), 200