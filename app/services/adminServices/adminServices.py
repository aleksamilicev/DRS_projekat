from flask import jsonify, request, current_app


def get_all_users():
    db_client = current_app.db_client  # Access db_client within the function
    query = "SELECT * FROM Licni_podaci_korisnika"
    results = db_client.execute_query(query)

    users = [{'id': row.id, 'ime': row.ime, 'prezime': row.prezime} for row in results]
    print(users)
    return jsonify({"message": "Retrieved all users", "users": users}), 200

def create_user():
   # To do
    user_data = request.get_json()
    return jsonify({"message": "User created successfully", "user": user_data}), 201

def block_user(user_id):
    # To do
    return jsonify({"message": f"User {user_id} blocked successfully"}), 200

def unblock_user(user_id):
    # To do
    return jsonify({"message": f"User {user_id} unblocked successfully"}), 200

def get_pending_posts():
    # To do
    return jsonify({"message": "Retrieved pending posts"}), 200

def approve_post(post_id):
    # To do
    return jsonify({"message": f"Post {post_id} approved successfully"}), 200

def reject_post(post_id):
    # To do
    return jsonify({"message": f"Post {post_id} rejected successfully"}), 200