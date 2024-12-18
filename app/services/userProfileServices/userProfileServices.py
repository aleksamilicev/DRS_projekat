# from flask import jsonify, request

# # Users route functions
# def get_user_profile(user_id):
#     # To do
#     return jsonify({"message": f"Retrieved profile for user {user_id}"}), 200

# def update_user_profile(user_id):
#     ## To do
#     return jsonify({"message": f"Updated profile for user {user_id}"}), 200

# def delete_user_profile(user_id):
#     # To do
#     return jsonify({"message": f"Deleted profile for user {user_id}"}), 200

from flask import jsonify, request, current_app
from app.utils import JWTManager
from flask_jwt_extended import jwt_required, get_jwt_identity
def get_user_profile(user_id):

    db_client = current_app.db_client
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)

    if(payload): 
        try:
            # Query to get user details from Licni_podaci_korisnika and related tables
            query = """
            SELECT 
                lpk.ID, 
                lpk.Ime, 
                lpk.Prezime, 
                ak.Ulica, 
                ak.Grad, 
                ak.Drzava, 
                ck.Broj_telefona, 
                ck.Email, 
                nk.Korisnicko_ime, 
                nk.Tip_korisnika, 
                nk.Blokiran
            FROM Licni_podaci_korisnika lpk
            LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID
            LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID
            LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID
            WHERE lpk.ID = :user_id
            """

            # Execute the query
            result = db_client.execute(query, {"user_id": user_id})

            if not result:
                return jsonify({"error": "User not found"}), 404

            # Format the response
            user_data = {
                "id": result[0][0],
                "first_name": result[0][1],
                "last_name": result[0][2],
                "address": {
                    "street": result[0][3],
                    "city": result[0][4],
                    "country": result[0][5],
                },
                "contact": {
                    "phone": result[0][6],
                    "email": result[0][7],
                },
                "account": {
                    "username": result[0][8],
                    "user_type": result[0][9],
                    "blocked": bool(result[0][10]),
                }
            }

            return jsonify(user_data), 200

        except Exception as e:
            current_app.logger.error(f"Error retrieving user profile for {user_id}: {str(e)}")
            return jsonify({"error": "Failed to retrieve user profile"}), 500
    else:
        return jsonify({"error": "No token provided"}), 400



def update_user_profile(user_id):
    db_client = current_app.db_client
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if(payload): 
        #debugging purposes
        #print(payload)
        current_user_id = payload["id"]
        # Ensure the user can only update their own profile
        if int(current_user_id) != int(user_id):
            return jsonify({"error": "You are not authorized to update this profile"}), 403

        try:
            data = request.get_json()
            updates = []

            # Prepare the updates for Licni_podaci_korisnika
            if "first_name" in data:
                updates.append(("Ime", data["first_name"]))
            if "last_name" in data:
                updates.append(("Prezime", data["last_name"]))

            for column, value in updates:
                query = f"UPDATE Licni_podaci_korisnika SET {column} = :value WHERE ID = :user_id"
                db_client.execute(query, {"value": value, "user_id": user_id})

            # Update Adresa_korisnika
            if "address" in data:
                address = data["address"]
                query = """
                UPDATE Adresa_korisnika 
                SET Ulica = :street, Grad = :city, Drzava = :country 
                WHERE ID = :user_id
                """
                db_client.execute(query, {
                    "street": address.get("street"),
                    "city": address.get("city"),
                    "country": address.get("country"),
                    "user_id": user_id
                })

            # Update Contact_korisnika
            if "contact" in data:
                contact = data["contact"]
                query = """
                UPDATE Contact_korisnika 
                SET Broj_telefona = :phone, Email = :email 
                WHERE ID = :user_id
                """
                db_client.execute(query, {
                    "phone": contact.get("phone"),
                    "email": contact.get("email"),
                    "user_id": user_id
                })

            return jsonify({"message": "Profile updated successfully"}), 200

        except Exception as e:
            current_app.logger.error(f"Error updating user profile {user_id}: {str(e)}")
            return jsonify({"error": "Failed to update user profile"}), 500
    else:
        return jsonify({"error": "No token provided"}), 400



def delete_user_profile(user_id):
    db_client = current_app.db_client
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)

    if(payload): 

    # Ensure the user can only delete their own profile
        current_user_id = payload["id"]
        # if int(current_user_id) != int(user_id):
        #     return jsonify({"error": "You are not authorized to delete this profile"}), 403

        try:
            # Delete from dependent tables first due to foreign key constraints
            db_client.execute("UPDATE Nalog_korisnika SET ISDELETED = 1 WHERE ID = :user_id",{"user_id": user_id})

            return jsonify({"message": "Profile deleted successfully"}), 200

        except Exception as e:
            current_app.logger.error(f"Error deleting user profile {user_id}: {str(e)}")
            return jsonify({"error": "Failed to delete user profile"}), 500
    else:
        return jsonify({"error": "No token provided"}), 400
