from flask import jsonify, request, current_app
from app.utils import JWTManager

#/notifications POST
def create_notification():
    """
    Create a new notification by inserting into Osnovni_podaci_notifikacije and Sadrzaj_notifikacije tables.
    """
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if payload:
        try:
            db_client = current_app.db_client
            
            data = request.get_json()
            id_korisnika = data.get("ID_Korisnika")
            status = data.get("Status")
            tekst = data.get("Tekst")
            
            # Insert into Osnovni_podaci_notifikacije
            osnovni_podaci_query = """
                INSERT INTO Osnovni_podaci_notifikacije (ID, ID_Korisnika, Status)
                VALUES (Notifikacije_seq.NEXTVAL, :id_korisnika, :status)
                RETURNING ID INTO :osnovni_podaci_id
            """
            
            osnovni_podaci_id = db_client.var(int)
            db_client.execute(osnovni_podaci_query, {"id_korisnika": id_korisnika, "status": status, "osnovni_podaci_id": osnovni_podaci_id})
            
            # Insert into Sadrzaj_notifikacije
            sadrzaj_query = """
                INSERT INTO Sadrzaj_notifikacije (ID, Osnovni_podaci_ID, Tekst)
                VALUES (Sadrzaj_notifikacije_seq.NEXTVAL, :osnovni_podaci_id, :tekst)
            """
            db_client.execute(sadrzaj_query, {"osnovni_podaci_id": osnovni_podaci_id.getvalue(), "tekst": tekst})

            return jsonify({"message": "Notification created successfully", "notification_id": osnovni_podaci_id.getvalue()}), 201
        except Exception as e:
            return jsonify({"error": "Failed to create notification", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400

# /notifications GET
def get_notifications():
    """
    Retrieve all notifications with details.
    """
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if payload:
    
        try:
            db_client = current_app.db_client
            query = """
                SELECT n.ID, n.ID_Korisnika, n.Status, s.Tekst, s.Datum_vreme_slanja
                FROM Osnovni_podaci_notifikacije n
                JOIN Sadrzaj_notifikacije s ON n.ID = s.Osnovni_podaci_ID
            """
            result = db_client.execute(query)
            notifications = [
                {
                    "ID": row[0],
                    "ID_Korisnika": row[1],
                    "Status": row[2],
                    "Tekst": row[3],
                    "Datum_vreme_slanja": row[4]
                }
                for row in result
            ]
            return jsonify(notifications), 200
        except Exception as e:
            return jsonify({"error": "Failed to retrieve notifications", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400


# /notifications/<int:notification_id> GET
def get_notification_by_id(notification_id):
    """
    Retrieve a single notification by its ID.
    """
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if payload:
    
        try:
            db_client = current_app.db_client
            query = """
                SELECT n.ID, n.ID_Korisnika, n.Status, s.Tekst, s.Datum_vreme_slanja
                FROM Osnovni_podaci_notifikacije n
                JOIN Sadrzaj_notifikacije s ON n.ID = s.Osnovni_podaci_ID
                WHERE n.ID = :notification_id
            """
            result = db_client.execute(query, {"notification_id": notification_id})
            
            if result:
                notification = {
                    "ID": result[0],
                    "ID_Korisnika": result[1],
                    "Status": result[2],
                    "Tekst": result[3],
                    "Datum_vreme_slanja": result[4]
                }
                return jsonify(notification), 200
            else:
                return jsonify({"error": f"No notification found with ID {notification_id}"}), 404
        except Exception as e:
            return jsonify({"error": "Failed to retrieve notification", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400


# /notifications/<int:notification_id> PUT
def update_notification(notification_id):
    """
    Update the status and text of a notification.
    """
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if payload:
    
        try:
            db_client = current_app.db_client
            data = request.get_json()
            status = data.get("Status")
            tekst = data.get("Tekst")
            
            # Update Osnovni_podaci_notifikacije
            db_client.execute("""
                UPDATE Osnovni_podaci_notifikacije 
                SET Status = :status 
                WHERE ID = :notification_id
            """, {"status": status, "notification_id": notification_id})
            
            # Update Sadrzaj_notifikacije
            db_client.execute("""
                UPDATE Sadrzaj_notifikacije 
                SET Tekst = :tekst 
                WHERE Osnovni_podaci_ID = :notification_id
            """, {"tekst": tekst, "notification_id": notification_id})

            return jsonify({"message": f"Notification {notification_id} updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Failed to update notification", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400


# /notifications/<int:notification_id>/read PUT
def mark_notification_as_read(notification_id):
    """
    Mark a notification's status as 'Read'.
    """
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if payload:
    
        try:
            db_client = current_app.db_client
            query = """
                UPDATE Osnovni_podaci_notifikacije
                SET Status = 'Read'
                WHERE ID = :notification_id
            """
            db_client.execute(query, {"notification_id": notification_id})
            return jsonify({"message": f"Notification {notification_id} marked as read"}), 200
        except Exception as e:
            return jsonify({"error": "Failed to mark notification as read", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400


# /notifications/<int:notification_id> DELETE
def delete_notification(notification_id):
    """
    Delete a notification.
    """
    jwt_manager = JWTManager()
    
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if payload:
        try:
            db_client = current_app.db_client
            # Delete from Sadrzaj_notifikacije first
            db_client.execute("""
                DELETE FROM Sadrzaj_notifikacije 
                WHERE Osnovni_podaci_ID = :notification_id
            """, {"notification_id": notification_id})

            # Delete from Osnovni_podaci_notifikacije
            db_client.execute("""
                DELETE FROM Osnovni_podaci_notifikacije 
                WHERE ID = :notification_id
            """, {"notification_id": notification_id})

            return jsonify({"message": f"Notification {notification_id} deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Failed to delete notification", "details": str(e)}), 500
    else:
        return jsonify({"error": "No token provided"}), 400
