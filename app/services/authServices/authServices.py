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

    # Hash the password with a salt
    hashed_password = generate_password_hash(lozinka)

    try:
        db_client.begin()

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

        # Insert user data into the database
        db_client.execute(
            "INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime) VALUES (Licni_podaci_seq.NEXTVAL, :ime, :prezime)",
            {"ime": ime, "prezime": prezime}
        )
        licni_id = db_client.execute("SELECT Licni_podaci_seq.CURRVAL FROM dual")[0][0]

        db_client.execute(
            "INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava) VALUES (:id, :ulica, :grad, :drzava)",
            {"id": licni_id, "ulica": ulica, "grad": grad, "drzava": drzava}
        )
        db_client.execute(
            "INSERT INTO Contact_korisnika (ID, Email, Broj_telefona) VALUES (:id, :email, :broj_telefona)",
            {"id": licni_id, "email": email, "broj_telefona": broj_telefona}
        )
        db_client.execute(
            "INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika) VALUES (:id, :korisnicko_ime, :lozinka, 'pendding')",
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

    query = "SELECT ID, Korisnicko_ime, Lozinka FROM Nalog_korisnika WHERE Korisnicko_ime = :korisnicko_ime"
    result = db_client.execute(query, {"korisnicko_ime": korisnicko_ime})

    if not result:
        return jsonify({"error": "Invalid username or password"}), 401

    user = result[0]
    user_id = user[0]
    db_password = user[2]

    # Verify the password
    if not check_password_hash(db_password, lozinka):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate JWT token
    access_token = create_access_token(
    identity=str(user_id),
    additional_claims={"username": korisnicko_ime},
    expires_delta=timedelta(days=30)  # Set token expiration to 30 days
)

    return jsonify({"token": access_token}), 200

def logout():
    
    return jsonify({"message": "User successfully logged out"}), 200

#     """
#     Simulacija odjavljivanja korisnika.
#     Klijent je odgovoran da prestane koristiti token nakon uspešnog logout-a.
#     """
#     auth_header = request.headers.get("Authorization")
#     if not auth_header or not auth_header.startswith("Bearer "):
#         return jsonify({"error": "Authorization token is missing or invalid"}), 401

#     return jsonify({"message": "User successfully logged out"}), 200




# # verzija sa blacklistom kao novom tabelom
# """
# def logout():
#     db_client = current_app.db_client  # Pristup bazi podataka
#     jwt_manager = JWTManager()  # Inicijalizacija JWTManager-a

#     # Dohvatanje tokena iz zaglavlja
#     auth_header = request.headers.get("Authorization")
#     if not auth_header or not auth_header.startswith("Bearer "):
#         return jsonify({"error": "Authorization token is missing or invalid"}), 401

#     token = auth_header.split(" ")[1]

#     try:
#         # Dodavanje tokena u blacklist (primer sa bazom podataka)
#         query = "INSERT INTO TokenBlacklist (token) VALUES (:token)"
#         db_client.execute_query(query, {"token": token})

#         return jsonify({"message": "User successfully logged out"}), 200

#     except Exception as e:
#         # Obrada grešaka
#         current_app.logger.error(f"Error during logout: {e}")
#         return jsonify({"error": "Internal server error"}), 500
# """


# def login():
#     db_client = current_app.db_client  # Pristup bazi podataka iz Flask aplikacije
#     jwt_manager = JWTManager()  # Inicijalizacija JWTManager-a

#     # Dohvatanje podataka iz zahteva
#     data = request.get_json()
#     korisnicko_ime = data.get("korisnicko_ime")
#     lozinka = data.get("lozinka")

#     if not korisnicko_ime:
#         return jsonify({"error": "Korisnicko ime is required"}), 400

#     if not lozinka:
#         return jsonify({"error": "Lozinka is required"}), 400

#     try:
#         # Provera da li korisnik postoji u bazi na osnovu korisnickog imena
#         query = "SELECT ID, Korisnicko_ime FROM Nalog_korisnika WHERE Korisnicko_ime = :korisnicko_ime AND Lozinka = :lozinka"
#         result = db_client.execute_query(query, {"korisnicko_ime": korisnicko_ime, "lozinka": lozinka})

#         if not result:
#             return jsonify({"error": "User does not exist"}), 404

#         user = result[0]  # Pretpostavka je da se korisnicko_ime vrednost ne ponavlja zbog UNIQUE ključa

#         # Generisanje JWT tokena
#         token = create_access_token(identity=str(user.id))

#         return jsonify({"message": "User found", "user_id": user.id, "korisnicko_ime": user.korisnicko_ime, "token": token}), 200

#     except Exception as e:
#         # Obrada grešaka
#         current_app.logger.error(f"Error during login: {e}")
#         return jsonify({"error": "Internal server error"}), 500