from flask import jsonify, request, current_app
from sqlalchemy import or_
#from config import db, Nalog_korisnika, Licni_podaci_korisnika, Prijateljstva
from flask_jwt_extended import get_jwt_identity, jwt_required



@jwt_required()
def get_suggestions():
    try:
        db_client = current_app.db_client
        current_user_id = get_jwt_identity()  # dobija ID trenutno ulogovanog korisnika

        query = """
            SELECT
                nk.ID,
                lpk.Ime,
                lpk.Prezime,
                nk.profile_picture_url,
                nk.Blokiran
            FROM Nalog_korisnika nk
            INNER JOIN Licni_podaci_korisnika lpk ON nk.ID = lpk.ID
            WHERE nk.ID != :current_user_id
              AND nk.Tip_korisnika = 'user'          -- ⬅︎ isključi admine
        """
        results = db_client.execute_query(query, {'current_user_id': current_user_id})

        users = [{
            'id': row[0],
            'ime': row[1],
            'prezime': row[2],
            'profile_picture_url': row[3],
            'blokiran': row[4]
        } for row in results]

        return jsonify({"message": "Retrieved all users", "users": users}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to retrieve users", "details": str(e)}), 500



def get_current_user_id():
    # Assuming you're using Flask-JWT or similar
    try:
        current_user_id = get_jwt_identity()
        return current_user_id
    except Exception as e:
        current_app.logger.error(f"Error getting current user ID: {e}")
        return None

@jwt_required()
def get_friends():
    db = current_app.db_client
    try:
        current_user_id = get_current_user_id()
        if not current_user_id:
            return jsonify({"error": "Unauthorized"}), 401

        query = """
        SELECT 
            lpk.ID                AS friend_id,
            lpk.Ime               AS first_name,
            lpk.Prezime           AS last_name,
            ck.Email              AS email,
            ck.Broj_telefona      AS phone_number,
            nk.Korisnicko_ime     AS username,            -- ⬅︎ dodaj kolonu
            p.Status              AS friendship_status
        FROM Prijateljstva p
        JOIN Licni_podaci_korisnika lpk 
             ON (CASE WHEN p.ID_Korisnika1 = :uid THEN p.ID_Korisnika2
                      ELSE p.ID_Korisnika1 END) = lpk.ID
        JOIN Contact_korisnika ck  ON lpk.ID = ck.ID
        JOIN Nalog_korisnika   nk  ON lpk.ID = nk.ID        -- ⬅︎ JOIN da dobiješ username
        WHERE (p.ID_Korisnika1 = :uid OR p.ID_Korisnika2 = :uid)
          AND p.Status = 'Accepted'
        """
        rows = db.execute_query(query, {"uid": current_user_id})

        friends = []
        seen = set()
        for r in rows:          # r je tuple
            fid = r[0]
            if fid in seen:
                continue
            seen.add(fid)
            friends.append({
                "id"              : fid,
                "first_name"      : r[1],
                "last_name"       : r[2],
                "email"           : r[3],
                "phone_number"    : r[4],
                "username"        : r[5],   # ⬅︎ ubaci u izlaz
                "friendship_status": r[6],
            })

        return jsonify({
            "message"      : "Friends retrieved successfully",
            "friends"      : friends,
            "total_friends": len(friends)
        }), 200

    except Exception as e:
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
    """
    • INSERT novi red ako ne postoji nijedan between users
    • Ako postoji:
        - Accepted  → 400
        - Pending   → 400
        - Rejected  → 
            » ako je isti pošiljalac → UPDATE status='Pending'
            » ako je pošiljalac obrnut → UPDATE swap kolone + status='Pending'
    """
    try:
        db   = current_app.db_client
        me   = int(get_jwt_identity())
        other = int(user_id)

        if me == other:
            return jsonify({"error": "Cannot send friend request to yourself"}), 400

        # provjeri da li drugi korisnik postoji
        if db.execute_query(
            "SELECT COUNT(*) FROM Nalog_korisnika WHERE ID = :uid", {"uid": other}
        )[0][0] == 0:
            return jsonify({"error": f"User {other} not found"}), 404

        # da li već postoji veza?
        row = db.execute_query(
            """
            SELECT ID, STATUS, ID_Korisnika1, ID_Korisnika2
            FROM   Prijateljstva
            WHERE (ID_Korisnika1 = :me AND ID_Korisnika2 = :other)
               OR (ID_Korisnika2 = :me AND ID_Korisnika1 = :other)
            """,
            {"me": me, "other": other}
        )

        if row:
            rel_id, status, sender_id, receiver_id = row[0]
            status = status.upper()

            if status == 'ACCEPTED':
                return jsonify({"error": "Users are already friends"}), 400

            if status == 'PENDING':
                return jsonify({"error": "Friend request already pending"}), 400

            if status == 'REJECTED':
                if sender_id == me:
                    # isti pošiljalac ponovo šalje → samo digni status
                    db.execute(
                        "UPDATE Prijateljstva SET STATUS = 'Pending' WHERE ID = :rid",
                        {"rid": rel_id}
                    )
                else:
                    # obrnuti smjer → zamijeni kolone i postavi na Pending
                    db.execute(
                        """
                        UPDATE Prijateljstva
                        SET ID_Korisnika1 = :me,
                            ID_Korisnika2 = :other,
                            STATUS        = 'Pending'
                        WHERE ID = :rid
                        """,
                        {"me": me, "other": other, "rid": rel_id}
                    )
                return jsonify({"message": "Friend request re‑sent"}), 200

        # nema nikakvog reda → INSERT novi
        db.execute(
            """
            INSERT INTO Prijateljstva
                   (ID, ID_Korisnika1, ID_Korisnika2, STATUS)
            VALUES (Prijateljstva_seq.NEXTVAL, :me, :other, 'Pending')
            """,
            {"me": me, "other": other}
        )
        return jsonify({"message": "Friend request sent successfully"}), 201

    except Exception as e:
        current_app.logger.error(f"Error sending friend request: {e}")
        return jsonify({"error": "Failed to send friend request"}), 500







@jwt_required()
def accept_friend_request(request_id):
    db_client = current_app.db_client
    
    try:
        # Get the current user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # First, verify the friend request exists and is intended for the current user
        verify_query = """
        SELECT ID_Korisnika1, ID_Korisnika2, Status 
        FROM Prijateljstva 
        WHERE ID_Korisnika1 = :request_id 
        AND ID_Korisnika2 = :current_user_id 
        AND Status = 'Pending'
        """
        
        friend_request = db_client.execute_query(
            verify_query, 
            {"request_id": request_id, "current_user_id": current_user_id}
        )
        
        # Check if the friend request exists
        if not friend_request:
            return jsonify({
                "error": "Friend request not found or already processed"
            }), 404
        
        # Update the friend request status to 'Accepted'
        update_query = """
        UPDATE Prijateljstva 
        SET Status = 'Accepted' 
        WHERE ID_Korisnika1 = :request_id
        """
        
        db_client.execute(update_query, {"request_id": request_id})
        
        return jsonify({
            "message": "Friend request accepted successfully"
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error accepting friend request: {str(e)}")
        return jsonify({"error": "Failed to accept friend request"}), 500




@jwt_required()
def reject_friend_request(request_id):
    db_client = current_app.db_client
    
    try:
        # Get the current user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # First, verify the friend request exists and is intended for the current user
        verify_query = """
        SELECT ID_Korisnika1, ID_Korisnika2, Status 
        FROM Prijateljstva 
        WHERE ID_Korisnika1 = :request_id 
        AND ID_Korisnika2 = :current_user_id 
        AND Status = 'Pending'
        """
        
        friend_request = db_client.execute_query(
            verify_query, 
            {"request_id": request_id, "current_user_id": current_user_id}
        )
        
        # Check if the friend request exists
        if not friend_request:
            return jsonify({
                "error": "Friend request not found or already processed"
            }), 404
        
        # Update the friend request status to 'Accepted'
        update_query = """
        UPDATE Prijateljstva 
        SET Status = 'Rejected' 
        WHERE ID_Korisnika1 = :request_id
        """
        
        db_client.execute(update_query, {"request_id": request_id})
        
        return jsonify({
            "message": "Friend request rejected successfully"
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error rejecting friend request: {str(e)}")
        return jsonify({"error": "Failed to reject friend request"}), 500




@jwt_required()
def delete_friend(friend_id):

    db_client = current_app.db_client
    try:
        # Dohvatanje ID-a trenutnog korisnika
        current_user_id = get_jwt_identity()
        # Provera da li je prijateljstvo već uspostavljeno
        check_query = """
        SELECT ID
        FROM Prijateljstva
        WHERE 
            (ID_Korisnika1 = :current_user_id AND ID_Korisnika2 = :friend_id)
            OR (ID_Korisnika1 = :friend_id AND ID_Korisnika2 = :current_user_id)
        """
        friendship = db_client.execute_query(
            check_query, {"current_user_id": current_user_id, "friend_id": friend_id}
        )

        if not friendship:
            return jsonify({"error": "Friendship not found or not accepted"}), 404

        # Brisanje prijateljstva
        delete_query = """
        DELETE FROM Prijateljstva
        WHERE 
            (ID_Korisnika1 = :current_user_id AND ID_Korisnika2 = :friend_id)
            OR (ID_Korisnika1 = :friend_id AND ID_Korisnika2 = :current_user_id)
        """
        db_client.execute(
            delete_query, {"current_user_id": current_user_id, "friend_id": friend_id}
        )
        
        return jsonify({"message": "Friend deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting friend: {str(e)}")
        return jsonify({"error": "Failed to delete friend"}), 500
