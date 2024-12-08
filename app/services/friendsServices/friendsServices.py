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
            Nalog_korisnika nk ON 
            (p.ID_Korisnika1 = :user_id OR p.ID_Korisnika2 = :user_id)
        JOIN 
            Licni_podaci_korisnika lpk ON 
            (CASE 
                WHEN p.ID_Korisnika1 = :user_id THEN p.ID_Korisnika2
                ELSE p.ID_Korisnika1
            END) = lpk.ID
        JOIN 
            Contact_korisnika ck ON lpk.ID = ck.ID
        WHERE 
            p.Status = 'Accepted'
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





def send_friend_request(user_id):
    return jsonify({"message": f"Friend request sent to user {user_id}!"}), 201




def get_friend_requests():
    return jsonify({"message": "List of friend requests"}), 200




def accept_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} accepted!"}), 200




def reject_friend_request(request_id):
    return jsonify({"message": f"Friend request {request_id} rejected!"}), 200






def delete_friend(friend_id):
    return jsonify({"message": f"Friend {friend_id} deleted!"}), 200