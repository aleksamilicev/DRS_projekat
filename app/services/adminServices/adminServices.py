from flask import jsonify, request, current_app
from app.utils import JWTManager

def get_all_blocked_users():
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    
    if(payload): 
        db_client = current_app.db_client  # Access db_client within the function
        query = "SELECT lpk.ID, lpk.Ime, lpk.Prezime, ak.Ulica, ak.Grad, ak.Drzava, ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, nk.Blokiran FROM Licni_podaci_korisnika lpk LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID WHERE nk.Status = 'blocked'"

        results = db_client.execute_query(query)

        users = [{'id': row.id, 'ime': row.ime, 'prezime': row.prezime} for row in results]
        print(users)
        return jsonify({"message": "Retrieved all users", "users": users}), 200
    else:
        return jsonify({"error": "No token provided"}), 400

#/admin/users GET
def get_all_users():
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    
    if(payload): 
        db_client = current_app.db_client  # Access db_client within the function
        query = "SELECT lpk.ID, lpk.Ime, lpk.Prezime, ak.Ulica, ak.Grad, ak.Drzava, ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, nk.Blokiran FROM Licni_podaci_korisnika lpk LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID"

        results = db_client.execute_query(query)

        users = [{'id': row.id, 'ime': row.ime, 'prezime': row.prezime} for row in results]
        print(users)
        return jsonify({"message": "Retrieved all users", "users": users}), 200
    else:
        return jsonify({"error": "No token provided"}), 400

def create_user():
   # To do
    user_data = request.get_json()
    return jsonify({"message": "User created successfully", "user": user_data}), 201
#/admin/users/<int:user_id>/block' POST
def block_user(user_id):
    """
    Block a user by setting BLOKIRAN to 1.
    """
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)
    
    if payload: 
        try:
            db_client = current_app.db_client  # Access db_client within the function
            
            # Update BLOKIRAN to 1 for the specified user
            db_client.execute(
                "UPDATE Nalog_korisnika SET BLOKIRAN = 1 WHERE ID = :user_id",
                {"user_id": user_id}
            )

            return jsonify({"message": f"User {user_id} blocked successfully"}), 200
        
        except Exception as e:
            return jsonify({"error": "An error occurred while blocking the user", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400
    
#/admin/users/<int:user_id>/unblock POST
def unblock_user(user_id):
    """
    Unblock a user by setting BLOKIRAN to 0 and resetting POST_REJECTED to 0.
    """
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)
    
    if payload: 
        try:
            db_client = current_app.db_client  # Access db_client within the function
            
            # Correct SQL query: Use a single SET clause with commas to separate fields
            db_client.execute(
                """
                UPDATE Nalog_korisnika 
                SET BLOKIRAN = 0, POST_REJECTED = 0 
                WHERE ID = :user_id
                """,
                {"user_id": user_id}
            )

            return jsonify({"message": f"User {user_id} unblocked successfully"}), 200
        
        except Exception as e:
            return jsonify({"error": "An error occurred while unblocking the user", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400
#/admin/posts/pending GET
def get_pending_posts():
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)
    
    if payload:
        print(payload)
        db_client = current_app.db_client  # Pristup bazi kroz db_client
        
        query = "SELECT opo.ID AS post_id, so.Tekst, so.Slika FROM Osnovni_podaci_objave opo LEFT JOIN Sadrzaj_objave so ON so.Osnovni_podaci_ID = opo.ID WHERE opo.Status = 'rejected'"
                
        pending_posts = []
        result = db_client.execute(query)  # Pretpostavka da db_client ima fetch_all
        for row in result:
            pending_posts.append({
                "post_id": row[0],
                "content": row[1],
                "image": row[2]
            })
        return jsonify({"pending_posts": pending_posts}), 200
    else:
        return jsonify({"error": "No valid token provided"}), 400
#/admin/posts/<int:post_id>/approve POST
def approve_post(post_id):
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)
    
    if payload:
        db_client = current_app.db_client  # Pristup bazi podataka kroz db_client

        # SQL upit za ažuriranje statusa objave
        update_query = """
            UPDATE Osnovni_podaci_objave
            SET Status = 'Approved'
            WHERE ID = :post_id
        """
        try:
            rows_affected = db_client.execute(update_query, {"post_id": post_id})

            if rows_affected > 0:
                return jsonify({"message": f"Post {post_id} approved successfully"}), 200
            else:
                return jsonify({"error": f"Post with ID {post_id} not found"}), 404

        except Exception as e:
            return jsonify({"error": "An error occurred while approving the post", "details": str(e)}), 500
    else:
        return jsonify({"error": "No valid token provided"}), 400

#/admin/posts/<int:post_id>/reject POST
def reject_post(post_id):
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)
    
    if payload:
        db_client = current_app.db_client  # Access the database client
        
        # Queries
        update_post_query = """
            UPDATE Osnovni_podaci_objave
            SET Status = 'Rejected'
            WHERE ID = :post_id
        """
        get_user_query = """
            SELECT ID_Korisnika
            FROM Osnovni_podaci_objave
            WHERE ID = :post_id
        """
        increment_rejected_posts_query = """
            UPDATE Nalog_korisnika
            SET POST_REJECTED = POST_REJECTED + 1
            WHERE ID = :user_posted
        """
        check_rejected_posts_query = """
            SELECT POST_REJECTED
            FROM Nalog_korisnika
            WHERE ID = :user_posted
        """
        
        try:
            # 1. Update post status
            db_client.execute(update_post_query, {"post_id": post_id})

            # 2. Fetch the user who created the post
            user_result = db_client.execute_query(get_user_query, {"post_id": post_id})
            
            if not user_result:  # No user found
                return jsonify({"error": f"Post with ID {post_id} not found"}), 404
            
            user_id = user_result[0]["ID_Korisnika"]  # Access the result as a dictionary

            # 3. Increment rejected posts for the user
            db_client.execute(increment_rejected_posts_query, {"user_posted": user_id})

            # 4. Check if POST_REJECTED >= 3
            rejected_count_result = db_client.execute_query(check_rejected_posts_query, {"user_posted": user_id})
            if not rejected_count_result:
                return jsonify({"error": "Failed to retrieve rejected post count"}), 500

            rejected_count = rejected_count_result[0]["POST_REJECTED"]

            # 5. Block user if POST_REJECTED >= 3
            if rejected_count >= 3:
                block_user(user_id)  # Call the block method (assumed to be implemented)
                return jsonify({"message": f"Post {post_id} rejected and user {user_id} has been blocked"}), 200

            return jsonify({"message": f"Post {post_id} rejected successfully"}), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "An error occurred while rejecting the post", "details": str(e)}), 500
    else:
        return jsonify({"error": "No valid token provided"}), 400
