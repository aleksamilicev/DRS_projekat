from flask import jsonify, request, current_app
from sqlalchemy import or_
#from config import db, Nalog_korisnika, Licni_podaci_korisnika, Prijateljstva
import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required


secret_key = "nas_secret_key_koji_bi_trebalo_da_se_nalazi_u_nekom_config_fileu" # da li ovo sluzi da decriptujemo hes iz polja lozinka?
class JWTManager:
    def __init__(self, algorithm="HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, payload):
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token):
        try:
            decoded_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded_payload
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")



def get_current_user_id():
    # Assuming you're using Flask-JWT or similar
    try:
        current_user_id = get_jwt_identity()
        return current_user_id
    except Exception as e:
        current_app.logger.error(f"Error getting current user ID: {e}")
        return None

@jwt_required()  # Obezbeđuje da se JWT token validira pre poziva funkcije
def get_friends():
    db_client = current_app.db_client  # Access to the database from the Flask application
    
    try:
        # Get the authenticated user's ID from the JWT token
        # Assuming you have a method to get the current user's ID from the token
        current_user_id = get_current_user_id()  # You'll need to implement this method
        
        if not current_user_id:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Query to fetch friends with their personal details
        query = """
        SELECT 
            lpk.ID AS friend_id,
            lpk.Ime AS first_name, 
            lpk.Prezime AS last_name,
            ck.Email AS email,
            ck.Broj_telefona AS phone_number,
            p.Status AS friendship_status
        FROM 
            Prijateljstva p
        JOIN 
            Licni_podaci_korisnika lpk 
            ON (CASE 
                    WHEN p.ID_Korisnika1 = :user_id THEN p.ID_Korisnika2
                    ELSE p.ID_Korisnika1
                END) = lpk.ID
        JOIN 
            Contact_korisnika ck 
            ON lpk.ID = ck.ID
        WHERE 
            (p.ID_Korisnika1 = :user_id OR p.ID_Korisnika2 = :user_id) 
            AND p.Status = 'Accepted'
        """
        
        # Execute the query
        friends = db_client.execute_query(query, {"user_id": current_user_id})
        seen_friends = set()  # Set to keep track of unique friends based on their ID
        friends_list = []
        
        # Transform the results into a list of dictionaries
        for friend in friends:
            if friend.friend_id not in seen_friends:
                seen_friends.add(friend.friend_id)
                friends_list.append({
                    "id": friend.friend_id,
                    "first_name": friend.first_name,
                    "last_name": friend.last_name,
                    "email": friend.email,
                    "phone_number": friend.phone_number,
                    "friendship_status": friend.friendship_status,
        })
        
        return jsonify({
            "message": "Friends retrieved successfully",
            "friends": friends_list,
            "total_friends": len(friends_list)
        }), 200
    
    except Exception as e:
        # Error handling
        current_app.logger.error(f"Error retrieving friends: {e}")
        return jsonify({"error": "Internal server error"}), 500




@jwt_required()
def get_friend_requests():
    db_client = current_app.db_client
    try:
        # Dohvatanje ID-a trenutnog korisnika
        current_user_id = get_jwt_identity()

        # Upit za dobijanje liste zahteva za prijateljstvo
        query = """
        SELECT f.ID, f.ID_Korisnika1, u.Korisnicko_ime, p.Ime, p.Prezime
        FROM Prijateljstva f
        JOIN Nalog_korisnika u ON f.ID_Korisnika1 = u.ID
        JOIN Licni_podaci_korisnika p ON f.ID_Korisnika1 = p.ID
        WHERE f.ID_Korisnika2 = :current_user_id AND f.Status = 'Pending'
        """
        friend_requests = db_client.execute_query(query, {"current_user_id": current_user_id})

        # Formatiranje rezultata u JSON
        requests_list = [
            {
                "request_id": row[0],
                "user_id": row[1],
                "username": row[2],
                "first_name": row[3],
                "last_name": row[4]
            }
            for row in friend_requests
        ]

        return jsonify({"friend_requests": requests_list}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching friend requests: {str(e)}")
        return jsonify({"error": "Failed to fetch friend requests"}), 500



@jwt_required()
def send_friend_request(user_id):
    db_client = current_app.db_client
    try:
        # Dohvatanje ID-a trenutnog korisnika
        current_user_id = get_jwt_identity()

        # Provera da li korisnik sa datim user_id postoji
        query_check_user = "SELECT COUNT(*) FROM Nalog_korisnika WHERE ID = :user_id"
        user_exists = db_client.execute_query(query_check_user, {"user_id": user_id})[0][0]

        if user_exists == 0:
            return jsonify({"error": f"User with ID {user_id} does not exist"}), 404

        # Provera da li već postoji prijateljstvo ili zahtev
        query_check_friendship = """
        SELECT COUNT(*) 
        FROM Prijateljstva 
        WHERE (ID_Korisnika1 = :current_user_id AND ID_Korisnika2 = :user_id) 
           OR (ID_Korisnika1 = :user_id AND ID_Korisnika2 = :current_user_id)
        """
        existing_relationship = db_client.execute_query(
            query_check_friendship, 
            {"current_user_id": current_user_id, "user_id": user_id}
        )[0][0]

        if existing_relationship > 0:
            return jsonify({"error": "Friend request already sent or users are already friends"}), 400

        # Kreiranje novog zahteva za prijateljstvo
        insert_query = """
        INSERT INTO Prijateljstva (ID, ID_Korisnika1, ID_Korisnika2, Status)
        VALUES (Prijateljstva_seq.NEXTVAL, :current_user_id, :user_id, 'Pending')
        """
        # current_user_id = 4(ulogovan sam kao ana) i zahtev sam poslao na user_id = 2(zahtev je poslalti jovani)
        db_client.execute(insert_query, {"current_user_id": current_user_id, "user_id": user_id})

        return jsonify({"message": "Friend request sent successfully"}), 201

    except Exception as e:
        current_app.logger.error(f"Error sending friend request: {str(e)}")
        return jsonify({"error": "Failed to send friend request"}), 500





def accept_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} accepted!"}), 200




def reject_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} rejected!"}), 200




def delete_friend(friend_id):
    return jsonify({"message": f"Friend {friend_id} deleted!"}), 200