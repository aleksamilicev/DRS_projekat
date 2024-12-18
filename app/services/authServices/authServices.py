from flask import jsonify, request, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
import re
from sqlalchemy.exc import IntegrityError
# from utils import JWTManager kaze no module named utils pa cu ovde napraviti klasu jwtManager
import jwt
from sqlalchemy.sql import bindparam
import traceback
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import JWTManager

# secret_key = "nas_secret_key_koji_bi_trebalo_da_se_nalazi_u_nekom_config_fileu" # da li ovo sluzi da decriptujemo hes iz polja lozinka?

# class JWTManager:
#     def __init__(self, algorithm="HS256"):
#         self.secret_key = secret_key
#         self.algorithm = algorithm

#     def create_token(self, payload):
#         token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
#         return token

#     def verify_token(self, token):
#         try:
#             decoded_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
#             return decoded_payload
#         except jwt.InvalidTokenError:
#             raise ValueError("Invalid token")




def register():
    db_client = current_app.db_client  # Pristup bazi podataka
    # Dohvatanje podataka iz zahteva
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

    # Provera postojanje email-a i username-a pre registracije
    check_email_query = "SELECT COUNT(*) FROM Contact_korisnika WHERE Email = :email"
    email_count = db_client.execute(check_email_query, {"email": email})[0][0]
    
    check_username_query = "SELECT COUNT(*) FROM Nalog_korisnika WHERE Korisnicko_ime = :korisnicko_ime"
    username_count = db_client.execute(check_username_query, {"korisnicko_ime": korisnicko_ime})[0][0]

    if email_count > 0:
        return jsonify({"error": "Email already exists"}), 400
    
    if username_count > 0:
        return jsonify({"error": "Username already exists"}), 400

    if not all([ime, prezime, ulica, grad, drzava, email, broj_telefona, korisnicko_ime, lozinka]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        # Start transaction
        db_client.begin()

        # 1. Insert into Licni_podaci_korisnika
        licni_query = "INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime) VALUES (Licni_podaci_seq.NEXTVAL, :ime, :prezime)"
        db_client.execute(licni_query, {"ime": ime, "prezime": prezime})
        licni_id_query = "SELECT Licni_podaci_seq.CURRVAL FROM dual"
        licni_id = db_client.execute(licni_id_query)[0][0]

        # 2. Insert into Adresa_korisnika
        adresa_query = "INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava) VALUES (:id, :ulica, :grad, :drzava)"
        db_client.execute(adresa_query, {"id": licni_id, "ulica": ulica, "grad": grad, "drzava": drzava})

        # 3. Insert into Contact_korisnika
        contact_query = "INSERT INTO Contact_korisnika (ID, Email, Broj_telefona) VALUES (:id, :email, :broj_telefona)"
        db_client.execute(contact_query, {"id": licni_id, "email": email, "broj_telefona": broj_telefona})

        # 4. Insert into Nalog_korisnika
        # IMPORTANT: In production, use password hashing (e.g., with bcrypt)
        nalog_query = "INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika) VALUES (:id, :korisnicko_ime, :lozinka, 'user')"
        db_client.execute(nalog_query, {"id": licni_id, "korisnicko_ime": korisnicko_ime, "lozinka": lozinka})

        # Commit the transaction
        db_client.commit()

        return jsonify({"message": "User successfully registered", "user_id": licni_id}), 201

    except Exception as e:
        # Rollback in case of any error
        db_client.rollback()
        
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


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
def login():
    db_client = current_app.db_client  # Access the database
    jwt_manager = JWTManager()  # Initialize JWTManager

    data = request.get_json()
    korisnicko_ime = data.get("korisnicko_ime")
    lozinka = data.get("lozinka")

    if not korisnicko_ime:
        return jsonify({"error": "Korisnicko ime is required"}), 400

    if not lozinka:
        return jsonify({"error": "Lozinka is required"}), 400

    try:
        query = "SELECT ID, Korisnicko_ime, Tip_Korisnika FROM Nalog_korisnika WHERE Korisnicko_ime = :korisnicko_ime AND Lozinka = :lozinka"
        result = db_client.execute_query(query, {"korisnicko_ime": korisnicko_ime, "lozinka": lozinka})

        if not result:
            return jsonify({"error": "User does not exist"}), 404

        user = result[0]

        # Generate a non-expirable JWT token
        payload = {
            "id": user.id,
            "korisnicko_ime": user.korisnicko_ime,
            "user_type": user.tip_korisnika
            # Other claims if necessary
        }
        print(user)
        token = jwt_manager.create_token(payload)

        return jsonify({"message": "User found", "user_id": user.id, "korisnicko_ime": user.korisnicko_ime, "token": token}), 200

    except Exception as e:
        current_app.logger.error(f"Error during login: {e}")
        return jsonify({"error": "Internal server error"}), 500


def logout():
    jwt_manager = JWTManager()
    payload = jwt_manager.extract_and_verify_token(request.headers)
    if(payload): 
        print("YIPIIII")
        print(payload)

         
        # Dodavanje tokena u blacklist (primer sa bazom podataka)
        
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