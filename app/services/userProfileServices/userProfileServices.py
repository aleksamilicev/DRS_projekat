from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import json

# Get user profile
@jwt_required()
def get_user_profile(user_id):
    db  = current_app.db_client
    me  = int(get_jwt_identity())       # ID of the logged‑in user
    uid = int(user_id)                  # ID we’re querying

    try:
        # 1️⃣ ── basic user info ────────────────────────────────────────────
        user_sql = """
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
        LEFT JOIN Adresa_korisnika  ak ON ak.ID = lpk.ID
        LEFT JOIN Contact_korisnika ck ON ck.ID = lpk.ID
        LEFT JOIN Nalog_korisnika   nk ON nk.ID = lpk.ID
        WHERE lpk.ID = :uid
        """
        u = db.execute(user_sql, {"uid": uid})
        if not u:
            return jsonify({"error": "User not found"}), 404
        u = u[0]

        # 2️⃣ ── counts ─────────────────────────────────────────────────────
        friends_cnt = db.execute(
            """
            SELECT COUNT(*)
            FROM Prijateljstva
            WHERE STATUS = 'Accepted'
              AND (ID_KORISNIKA1 = :uid OR ID_KORISNIKA2 = :uid)
            """,
            {"uid": uid},
        )[0][0]

        posts_cnt = db.execute(
            """
            SELECT COUNT(*)
            FROM Osnovni_podaci_objave
            WHERE ID_Korisnika = :uid
            """,  # add AND Status='Approved' if needed
            {"uid": uid},
        )[0][0]

        # 3️⃣ ── friend status between *me* and *uid* ──────────────────────
       # 3️⃣ ── friend status between *me* and *uid* ──────────────────────
        if me == uid:
            friend_status = "self"
            is_receiver = False
        else:
            fs = db.execute(
                """
                SELECT STATUS, ID_KORISNIKA2
                FROM Prijateljstva
                WHERE (ID_KORISNIKA1 = :me AND ID_KORISNIKA2 = :uid)
                OR (ID_KORISNIKA2 = :me AND ID_KORISNIKA1 = :uid)
                """,
                {"me": me, "uid": uid},
            )

            is_receiver = False  # ✅ Default value

            if fs:
                status, id2 = fs[0]
                friend_status = status
                is_receiver = (id2 == me)
            else:
                friend_status = "none"



        # 4️⃣ ── assemble response ─────────────────────────────────────────
        return (
            jsonify(
                {
                    "id": u[0],
                    "first_name": u[1],
                    "last_name": u[2],
                    "address": {"street": u[3], "city": u[4], "country": u[5]},
                    "contact": {"phone": u[6], "email": u[7]},
                    "account": {
                        "username": u[8],
                        "user_type": u[9],
                        "blocked": bool(u[10]),
                        "profile_picture_url": u[11],
                    },
                    "friends_count": friends_cnt,
                    "posts_count": posts_cnt,
                    "friend_status": friend_status,
                    "is_owner": me == uid,
                    "is_receiver": is_receiver,
                }
            ),
            200,
        )

    except Exception as exc:
        current_app.logger.error(f"Profile fetch error (uid={uid}): {exc}")
        return jsonify({"error": "Failed to retrieve profile"}), 500


# Update user profile
@jwt_required()
def update_user_profile(user_id):
    db = current_app.db_client

    # --- Auth: user can edit only own profile ---------------------------------
    current_user_id = get_jwt_identity()
    if int(current_user_id) != int(user_id):
        return jsonify({"error": "Not authorized"}), 403

    try:
        # ---------- 1) JSON body ------------------------------------------------
        data = request.get_json(force=True) or {}
        print(data)        # ---------- 2) Personal data -------------------------------------------
        if "first_name" in data:
            db.execute(
                "UPDATE Licni_podaci_korisnika SET Ime = :v WHERE ID = :id",
                {"v": data["first_name"], "id": user_id}
            )

        if "last_name" in data:
            db.execute(
                "UPDATE Licni_podaci_korisnika SET Prezime = :v WHERE ID = :id",
                {"v": data["last_name"], "id": user_id}
            )

        # ---------- 3) Address --------------------------------------------------
        if "address" in data:
            a = data["address"]
            db.execute(
                """
                UPDATE Adresa_korisnika
                   SET Ulica  = :u,
                       Grad   = :g,
                       Drzava = :d
                 WHERE ID = :id
                """,
                {"u": a.get("street"), "g": a.get("city"),
                 "d": a.get("country"), "id": user_id}
            )

        # ---------- 4) Contact --------------------------------------------------
        if "contact" in data:
            c = data["contact"]
            db.execute(
                """
                UPDATE Contact_korisnika
                   SET Broj_telefona = :p,
                       Email         = :e
                 WHERE ID = :id
                """,
                {"p": c.get("phone"), "e": c.get("email"), "id": user_id}
            )

        # ---------- 5) Profile‑picture URL -------------------------------------
        if "profile_picture_url" in data:
            db.execute(
                """
                UPDATE Nalog_korisnika
                   SET PROFILE_PICTURE_URL = :url
                 WHERE ID = :id
                """,
                {"url": data["profile_picture_url"], "id": user_id}
            )

        db.commit()
        return jsonify({"message": "Profile updated"}), 200

    except Exception as e:
        db.rollback()
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
