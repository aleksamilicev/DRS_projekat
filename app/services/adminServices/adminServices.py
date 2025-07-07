import os
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
            SELECT nk.ID, lpk.Ime, lpk.Prezime, ak.Ulica, ak.Grad, ak.Drzava, 
            ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, nk.Blokiran, nk.profile_picture_url
            FROM Nalog_korisnika nk
            INNER JOIN Licni_podaci_korisnika lpk ON nk.ID = lpk.ID
            INNER JOIN Adresa_korisnika ak ON nk.ID = ak.ID
            INNER JOIN Contact_korisnika ck ON nk.ID = ck.ID
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
                'profile_picture_url': row[11],
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
        #query = "UPDATE Nalog_korisnika SET TIP_KORISNIKA = 'user' WHERE ID = :user_id"
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
                   ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, nk.Blokiran, nk.profile_picture_url
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
                'profile_picture_url' : row[11],
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
        db_client = current_app.db_client  
        jwt_manager.checkIfAdmin(db_client)
        query = "UPDATE Nalog_korisnika SET TIP_KORISNIKA = 'user' WHERE ID = :user_id"
        db_client.execute(query, {"user_id": user_id})
        user = get_user_by_id(user_id)
        
        notify_user_by_email(user_id, EmailText.EmailText.register_approved(user['username']), db_client)
        return jsonify({"message": f"User {user_id} has been accepted"}), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to accept the user", "details": str(e)}), 500

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


def normalize_image_path(path):
    if not path:
        return None
    if path.startswith('/'):
        # već relativna putanja
        return request.host_url.rstrip('/') + path
    else:
        # pretpostavljamo da je apsolutna putanja na disku, izvuci samo ime fajla i napravi relativnu putanju
        filename = os.path.basename(path)
        return request.host_url.rstrip('/') + '/static/uploads/' + filename

@jwt_required()
def get_all_posts():
   
    jwt_manager = JWTManager()
    try:
        db_client = current_app.db_client  # Access the database client
        # Check if the user is an admin
        jwt_manager.checkIfAdmin(db_client)
        
        # Query for posts with user info
        query = """
            SELECT
                opo.ID AS post_id,
                so.Tekst AS content,
                so.Slika AS image,
                nk.Korisnicko_ime AS username,
                nk.profile_picture_url
            FROM Osnovni_podaci_objave opo
            LEFT JOIN Sadrzaj_objave so ON so.Osnovni_podaci_ID = opo.ID
            LEFT JOIN Nalog_korisnika nk ON opo.ID_Korisnika = nk.ID
        """

        results = db_client.execute_query(query)

        posts = [{
            'post_id': row[0],
            'content': row[1],
            'image': row[2],
            'username': row[3],
            'profile_picture_url': row[4]
        } for row in results]

        return jsonify({"posts": posts}), 200

    except PermissionError as e:
        
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to retrieve posts", "details": str(e)}), 500



#/admin/posts/pending GET
@jwt_required()
def get_pending_posts():
    jwt_manager = JWTManager()
    try:
        db_client = current_app.db_client
        
        # Provera admin privilegija
        jwt_manager.checkIfAdmin(db_client)
        
        query = """
            SELECT
                o.ID AS post_id,
                s.Tekst AS content,
                s.Slika AS image,
                n.Korisnicko_ime AS username,
                l.Ime AS first_name,
                l.Prezime AS last_name,
                n.PROFILE_PICTURE_URL as PROFILE_PICTURE_URL
            FROM
                Osnovni_podaci_objave o
            JOIN
                Sadrzaj_objave s ON o.ID = s.Osnovni_podaci_ID
            JOIN
                Nalog_korisnika n ON o.ID_Korisnika = n.ID
            JOIN
                Licni_podaci_korisnika l ON o.ID_Korisnika = l.ID
            WHERE
                o.Status = 'pending'
            ORDER BY
                o.ID DESC
        """
        
        results = db_client.execute_query(query)
        
        pending_posts = [
            {
                "post_id": row[0],
                "content": row[1],
                "image": row[2],
                "username": row[3],
                "first_name": row[4],
                "last_name": row[5],
                "profile_picture_url": row[6],
            }
            for row in results
        ]
        
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



#---Additional function used---#
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

def get_user_by_id(user_id):
    try:
        db_client = current_app.db_client  # Access the database client

        query = """
            SELECT lpk.ID, lpk.Ime, lpk.Prezime, ak.Ulica, ak.Grad, ak.Drzava, 
                   ck.Broj_telefona, ck.Email, nk.Korisnicko_ime, nk.Tip_korisnika, 
                   nk.Blokiran, nk.profile_picture_url
            FROM Licni_podaci_korisnika lpk
            LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID
            LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID
            LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID
            WHERE nk.ID = :user_id
        """

        rows = db_client.execute_query(query, {"user_id": user_id})

        if not rows:
            print(f"No user found with ID {user_id}")
            return None  

        row = rows[0] 

        user = {
            'id': row[0],
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
            'profile_picture_url': row[11],
        }

        return user

    except PermissionError as e:
        print({"error": str(e)})
    except Exception as e:
        print({
            "error": f"An error occurred while retrieving user with id: {user_id}",
            "details": str(e)
        })
        return None
