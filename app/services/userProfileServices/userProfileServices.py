from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import json

# Get user profile
@jwt_required()
def get_user_profile(user_id):
    db_client = current_app.db_client
    current_user_id = get_jwt_identity()  # Extract the ID of the current user from the token

    if int(current_user_id) != int(user_id):
        return jsonify({"error": "You are not authorized to view this profile"}), 403

    try:
        # Query to get user details from related tables
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
            nk.Blokiran,
            nk.PROFILE_PICTURE_URL
        FROM Licni_podaci_korisnika lpk
        LEFT JOIN Adresa_korisnika ak ON lpk.ID = ak.ID
        LEFT JOIN Contact_korisnika ck ON lpk.ID = ck.ID
        LEFT JOIN Nalog_korisnika nk ON lpk.ID = nk.ID
        WHERE lpk.ID = :user_id
        """
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
                "profile_picture_url": result[0][11],
            }
        }
        return jsonify(user_data), 200

    except Exception as e:
        current_app.logger.error(f"Error retrieving user profile for {user_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve user profile"}), 500


# Update user profile
@jwt_required()
def update_user_profile(user_id):
    db = current_app.db_client
    current_user = get_jwt_identity()
    if int(current_user) != int(user_id):
        return jsonify({"error": "Not authorized"}), 403

    try:
        # ①  JSON dio stiže u polju "data" (kao string)
        data_json = request.form.get("data", "{}")
        data = json.loads(data_json)

        # ②  Slika, ako je poslata
        pic = request.files.get("profile_picture")

        # -- licni podaci ---------------------------------------------------
        if "first_name" in data:
            db.execute("UPDATE Licni_podaci_korisnika SET Ime = :v WHERE ID = :id",
                       {"v": data["first_name"], "id": user_id})
        if "last_name" in data:
            db.execute("UPDATE Licni_podaci_korisnika SET Prezime = :v WHERE ID = :id",
                       {"v": data["last_name"], "id": user_id})

        # -- adresa ---------------------------------------------------------
        if "address" in data:
            a = data["address"]
            db.execute("""
                UPDATE Adresa_korisnika
                SET Ulica = :u, Grad = :g, Drzava = :d
                WHERE ID = :id
            """, {"u": a.get("street"), "g": a.get("city"),
                  "d": a.get("country"), "id": user_id})

        # -- kontakt --------------------------------------------------------
        if "contact" in data:
            c = data["contact"]
            db.execute("""
                UPDATE Contact_korisnika
                SET Broj_telefona = :p, Email = :e
                WHERE ID = :id
            """, {"p": c.get("phone"), "e": c.get("email"), "id": user_id})

        # -- profil‑slika ---------------------------------------------------
        if pic:
            filename = secure_filename(pic.filename)
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            pic.save(save_path)

            db.execute("""
                UPDATE Nalog_korisnika
                SET PROFILE_PICTURE_URL = :url
                WHERE ID = :id
            """, {"url": f"{request.url_root}static/uploads/{filename}", "id": user_id})

        return jsonify({"message": "Profile updated"}), 200

    except Exception as e:
        current_app.logger.error(f"Profile update {user_id}: {e}")
        return jsonify({"error": "Update failed"}), 500



# Delete user profile
@jwt_required()
def delete_user_profile(user_id):
    db_client = current_app.db_client
    current_user_id = get_jwt_identity()  # Extract the ID of the current user from the token

    # Ensure the user can only delete their own profile
    if int(current_user_id) != int(user_id):
        return jsonify({"error": "You are not authorized to delete this profile"}), 403

    try:
        # Soft delete the user by marking the profile as deleted
        query = "UPDATE Nalog_korisnika SET ISDELETED = 1 WHERE ID = :user_id"
        db_client.execute(query, {"user_id": user_id})

        return jsonify({"message": "Profile deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting user profile {user_id}: {str(e)}")
        return jsonify({"error": "Failed to delete user profile"}), 500
