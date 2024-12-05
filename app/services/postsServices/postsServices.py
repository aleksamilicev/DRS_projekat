from flask import jsonify, request

# Posts route functions
def create_post():
    # To do
    return jsonify({"message": "Post created successfully"}), 201

def get_post_by_id(post_id):
    # To do
    return jsonify({"message": f"Retrieved post {post_id}"}), 200

def update_post(post_id):
    # To do
    return jsonify({"message": f"Post {post_id} updated successfully"}), 200

def delete_post(post_id):
    # To do
    return jsonify({"message": f"Post {post_id} deleted successfully"}), 200

def get_friends_posts():
    # To do
    return jsonify({"message": "Retrieved friends' posts"}), 200
