from flask import jsonify, request, current_app
from app.utils import JWTManager
from flask_jwt_extended import jwt_required
from ...utils import send_email
from ...utils import EmailText
#/admin/users GET
@jwt_required()
def get_all_users():
    jwt_manager = JWTManager()
    
    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Query to get all users
        query = """
            SELECT lpk.ID, lpk.Ime, lpk.Prezime, ak.Ulica, ak.Grad, ak.Drzava, 
                   ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, nk.Blokiran
            FROM Licni_podaci_korisnika lpk
            LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID
            LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID
            LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID
        """
        results = db_client.execute_query(query)

        users = [{'id': row[0],
                'ime': row[1],
                'prezime': row[2],
                'ulica': row[3], 
                'grad': row[4], 
                'drzava': row[5], 
                'broj_telefon': row[6], 
                'email': row[7], 
                'username': row[8], 
                'tip_korisnika': row[9], 
                'blokiran': row[10],
                } for row in results]

        return jsonify({"message": "Retrieved all users", "users": users}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to retrieve users", "details": str(e)}), 500
    
#/admin/users/<int:user_id>/block' POST
@jwt_required()
def block_user(user_id):
    jwt_manager = JWTManager()

    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Block the user
        query = "UPDATE Nalog_korisnika SET BLOKIRAN = 1 WHERE ID = :user_id"
        db_client.execute(query, {"user_id": user_id})

        return jsonify({"message": f"User {user_id} blocked successfully"}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to block the user", "details": str(e)}), 500
    
@jwt_required()
def get_all_blocked_users():
    jwt_manager = JWTManager()
    
    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Query to retrieve all blocked users
        query = """
            SELECT lpk.ID, lpk.Ime, lpk.Prezime, ak.Ulica, ak.Grad, ak.Drzava, 
                   ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, nk.Blokiran
            FROM Licni_podaci_korisnika lpk
            LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID
            LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID
            LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID
            WHERE nk.Blokiran = 1
        """
        results = db_client.execute_query(query)

        users = [{'id': row[0],
                'ime': row[1],
                'prezime': row[2],
                'ulica': row[3], 
                'grad': row[4], 
                'drzava': row[5], 
                'broj_telefon': row[6], 
                'email': row[7], 
                'username': row[8], 
                'tip_korisnika': row[9], 
                'blokiran': row[10],
                } for row in results]
        
        return jsonify({"message": "Retrieved all blocked users", "users": users}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving blocked users", "details": str(e)}), 500
@jwt_required()
def get_pending_registrations():
    jwt_manager = JWTManager()
    
    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Query to retrieve all blocked users
        query = """
            SELECT lpk.ID, lpk.Ime, lpk.Prezime, ak.Ulica, ak.Grad, ak.Drzava, 
                   ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, nk.Blokiran
            FROM Licni_podaci_korisnika lpk
            LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID
            LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID
            LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID
            WHERE nk.Tip_Korisnika = 'pending'
        """
        results = db_client.execute_query(query)

        users = [{'id': row[0],
                'ime': row[1],
                'prezime': row[2],
                'ulica': row[3], 
                'grad': row[4], 
                'drzava': row[5], 
                'broj_telefon': row[6], 
                'email': row[7], 
                'username': row[8], 
                'tip_korisnika': row[9], 
                'blokiran': row[10],
                } for row in results]
        
        return jsonify({"message": "Retrieved all users with pending registration", "users": users}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving users with pending registration", "details": str(e)}), 500
@jwt_required()
def accept_registration(user_id):
    jwt_manager = JWTManager()

    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        querry = """
            UPDATE nalog_korisnika SET Tip_korisnika = 'user' WHERE ID = :user_id"
        """
        # Reject the post and handle user rejection count
        db_client.execute(querry, {"user_id": user_id})
        notify_user_by_email(user_id, EmailText.EmailText.register_approved(user_id), db_client)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    return
@jwt_required()
def reject_registration(user_id):
    jwt_manager = JWTManager()

    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        accept_registration(user_id)
        block_user(user_id)
        notify_user_by_email(user_id, EmailText.EmailText.register_rejected(user_id), db_client)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    return

def create_user():
   # To do
    user_data = request.get_json()
    return jsonify({"message": "User created successfully", "user": user_data}), 201
    
#/admin/users/<int:user_id>/unblock POST
@jwt_required()
def unblock_user(user_id):
    jwt_manager = JWTManager()

    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Unblock the user
        query = """
            UPDATE Nalog_korisnika 
            SET BLOKIRAN = 0, POST_REJECTED = 0 
            WHERE ID = :user_id
        """
        db_client.execute(query, {"user_id": user_id})

        return jsonify({"message": f"User {user_id} unblocked successfully"}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to unblock the user", "details": str(e)}), 500
#/admin/posts/pending GET
@jwt_required()
def get_pending_posts():
    jwt_manager = JWTManager()

    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Query for pending posts
        query = """
            SELECT opo.ID AS post_id, so.Tekst, so.Slika 
            FROM Osnovni_podaci_objave opo
            LEFT JOIN Sadrzaj_objave so ON so.Osnovni_podaci_ID = opo.ID
            WHERE opo.Status = 'rejected'
        """
        results = db_client.execute_query(query)
        
        pending_posts = [{'post_id': row[0], 'content': row[1], 'image': row[2]} for row in results]
        return jsonify({"pending_posts": pending_posts}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to retrieve pending posts", "details": str(e)}), 500

#/admin/posts/<int:post_id>/approve POST
@jwt_required()
def approve_post(post_id):
    jwt_manager = JWTManager()

    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # SQL query to update the post status to 'Approved'
        update_query = """
            UPDATE Osnovni_podaci_objave
            SET Status = 'Approved'
            WHERE ID = :post_id
        """
        
        rows_affected = db_client.execute(update_query, {"post_id": post_id})

        # Handle NoneType or zero rows affected
        if rows_affected and rows_affected > 0:
            return jsonify({"message": f"Post {post_id} approved successfully"}), 200
        else:
            return jsonify({"error": f"Post with ID {post_id} not found or not updated"}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "An error occurred while approving the post", "details": str(e)}), 500


@jwt_required()
def reject_post(post_id):
    jwt_manager = JWTManager()

    try:
        db_client = current_app.db_client  # Access the database client
        
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Reject the post and handle user rejection count
        db_client.execute("UPDATE Osnovni_podaci_objave SET Status = 'Rejected' WHERE ID = :post_id", {"post_id": post_id})

        user_result = db_client.execute_query("SELECT ID_Korisnika FROM Osnovni_podaci_objave WHERE ID = :post_id", {"post_id": post_id})
        if not user_result:
            return jsonify({"error": "Post not found"}), 404

        user_id = user_result[0][0]
        db_client.execute("UPDATE Nalog_korisnika SET POST_REJECTED = POST_REJECTED + 1 WHERE ID = :user_id", {"user_id": user_id})

        rejected_count_result = db_client.execute_query("SELECT POST_REJECTED FROM Nalog_korisnika WHERE ID = :user_id", {"user_id": user_id})
        if rejected_count_result[0][0] >= 3:
            block_user(user_id)

        return jsonify({"message": f"Post {post_id} rejected successfully"}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to reject the post", "details": str(e)}), 500
def notify_user_by_email(user_id, message: str, db_client):
    
    query = """
        SELECT Email
        FROM Contact_Korisnika
        WHERE ID = :user_id
    """
    results = db_client.execute_query(query, {"user_id": user_id})
    
    
    if results and results[0][0]:
        user_email = results[0][0]
        send_email(user_email, message)