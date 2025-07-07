from flask import jsonify, request, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import traceback
from ...utils import send_email
from ...utils import EmailText
from datetime import timedelta

def register():
    db_client = current_app.db_client
    data = request.get_json()
    ime = data.get("ime")
    prezime = data.get("prezime")
    ulica = data.get("ulica")
    grad = data.get("grad")
    drzava = data.get("drzava")
    email = data.get("email")
    broj_telefona = data.get("broj_telefona")
    korisnicko_ime = data.get("korisnicko_ime")
    lozinka = data.get("lozinka")

    if not all([ime, prezime, ulica, grad, drzava, email, broj_telefona, korisnicko_ime, lozinka]):
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = generate_password_hash(lozinka)

    try:
        # Check if email or username already exists
        email_count = db_client.execute(
            "SELECT COUNT(*) FROM Contact_korisnika WHERE Email = :email",
            {"email": email}
        )[0][0]
        if email_count > 0:
            return jsonify({"error": "Email already exists"}), 400

        username_count = db_client.execute(
            "SELECT COUNT(*) FROM Nalog_korisnika WHERE Korisnicko_ime = :korisnicko_ime",
            {"korisnicko_ime": korisnicko_ime}
        )[0][0]
        if username_count > 0:
            return jsonify({"error": "Username already exists"}), 400

        # Generate ID first, then use it in all inserts
        licni_id = db_client.execute("SELECT Licni_podaci_seq.NEXTVAL FROM dual")[0][0]

        # Insert user data using the generated ID
        db_client.execute(
            "INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime) VALUES (:id, :ime, :prezime)",
            {"id": licni_id, "ime": ime, "prezime": prezime}
        )

        db_client.execute(
            "INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava) VALUES (:id, :ulica, :grad, :drzava)",
            {"id": licni_id, "ulica": ulica, "grad": grad, "drzava": drzava}
        )

        db_client.execute(
            "INSERT INTO Contact_korisnika (ID, Email, Broj_telefona) VALUES (:id, :email, :broj_telefona)",
            {"id": licni_id, "email": email, "broj_telefona": broj_telefona}
        )

        db_client.execute(
            "INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika) VALUES (:id, :korisnicko_ime, :lozinka, 'pending')",
            {"id": licni_id, "korisnicko_ime": korisnicko_ime, "lozinka": hashed_password}
        )

        db_client.commit()
        
        send_email(email, EmailText.EmailText.register_pending(korisnicko_ime))
        return jsonify({"message": "User successfully registered", "user_id": licni_id}), 201

    except Exception as e:
        db_client.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


def login():
    db_client = current_app.db_client
    data = request.get_json()
    korisnicko_ime = data.get("korisnicko_ime")
    lozinka = data.get("lozinka")

    if not korisnicko_ime or not lozinka:
        return jsonify({"error": "Username and password are required"}), 400

    query = """
        SELECT ID, Korisnicko_ime, Lozinka, Tip_korisnika, BLOKIRAN, FIRST_TIME_LOGIN, profile_picture_url
        FROM Nalog_korisnika
        WHERE Korisnicko_ime = :korisnicko_ime
    """
    result = db_client.execute(query, {"korisnicko_ime": korisnicko_ime})

    if not result:
        return jsonify({"error": "Invalid username or password"}), 401

    user = result[0]
    user_id = user[0]
    username = user[1]
    db_password = user[2]
    user_role = user[3]
    blokiran = user[4]
    first_time_login = user[5]
    profile_picture_url = user[6]
    if user_role == "pending":
        return jsonify({"error": "Your account is not accepted by the admin yet."}), 403

    if blokiran == 1:
        return jsonify({"error": "Your account is blocked."}), 403

    if not check_password_hash(db_password, lozinka):
        return jsonify({"error": "Invalid username or password"}), 401

    # If first time login, notify all admins
    if first_time_login == 1:
        admin_email_query = """
            SELECT ck.Email
            FROM Nalog_korisnika nk
            JOIN Contact_korisnika ck ON nk.ID = ck.ID
            WHERE nk.Tip_korisnika = 'admin'
        """
        admin_emails = db_client.execute_query(admin_email_query)

        for row in admin_emails:
            email = row[0]
            if email:
                send_email(
                    email,
                    EmailText.EmailText.first_time_login_notification(username)
                )

        # Update FIRST_TIME_LOGIN to 0
        update_query = """
            UPDATE Nalog_korisnika
            SET FIRST_TIME_LOGIN = 0
            WHERE ID = :user_id
        """
        db_client.execute(update_query, {"user_id": user_id})

    # Generate JWT 
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={"username": korisnicko_ime, "role": user_role, "profile_picture_url": profile_picture_url},
        expires_delta=timedelta(days=30)
    )

    return jsonify({"token": access_token}), 200


def logout():
    
    return jsonify({"message": "User successfully logged out"}), 200
