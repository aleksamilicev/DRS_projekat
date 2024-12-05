from flask import jsonify, request, current_app
from werkzeug.security import generate_password_hash
import re
from sqlalchemy.exc import IntegrityError

def validate_email(email):
    """Validate email format using regex."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

from sqlalchemy.sql import bindparam

def register():
    db_client = current_app.db_client
    data = request.get_json()

    # Validate input data
    required_fields = [
        'ime', 'prezime', 'ulica', 'grad', 'drzava', 
        'broj_telefona', 'email', 'korisnicko_ime', 'lozinka', 'tip_korisnika'
    ]
    
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Email validation
    if not validate_email(data['email']):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        # Check unique constraints for username and email
        existing_username = db_client.execute_query(
            "SELECT COUNT(*) FROM Nalog_korisnika WHERE Korisnicko_ime = :username", 
            {"username": data['korisnicko_ime']}
        ).scalar_one_or_none()
        
        existing_email = db_client.execute_query(
            "SELECT COUNT(*) FROM Contact_korisnika WHERE Email = :email", 
            {"email": data['email']}
        ).scalar_one_or_none()

        if existing_username:
            return jsonify({"error": "Username already exists"}), 409
        
        if existing_email:
            return jsonify({"error": "Email already registered"}), 409

        # Start a transaction
        with db_client.begin() as connection:
            # Insert personal data and get the generated ID
            personal_data_insert = """
            INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime)
            VALUES (Licni_podaci_seq.NEXTVAL, :ime, :prezime)
            RETURNING ID
            """
            user_id = connection.execute_query(
                personal_data_insert, 
                {'ime': data['ime'], 'prezime': data['prezime']}
            ).scalar_one()

            # Insert address
            address_insert = """
            INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava)
            VALUES (:id, :ulica, :grad, :drzava)
            """
            connection.execute_query(address_insert, {
                'id': user_id,
                'ulica': data['ulica'],
                'grad': data['grad'],
                'drzava': data['drzava']
            })

            # Insert contact information
            contact_insert = """
            INSERT INTO Contact_korisnika (ID, Broj_telefona, Email)
            VALUES (:id, :broj_telefona, :email)
            """
            connection.execute_query(contact_insert, {
                'id': user_id,
                'broj_telefona': data['broj_telefona'],
                'email': data['email']
            })

            # Hash password before storing
            hashed_password = generate_password_hash(data['lozinka'])

            # Insert user account
            account_insert = """
            INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika, Blokiran)
            VALUES (:id, :korisnicko_ime, :lozinka, :tip_korisnika, 0)
            """
            connection.execute_query(account_insert, {
                'id': user_id,
                'korisnicko_ime': data['korisnicko_ime'],
                'lozinka': hashed_password,
                'tip_korisnika': data['tip_korisnika']
            })

        return jsonify({
            "message": "User registered successfully!", 
            "user_id": user_id
        }), 201

    except IntegrityError as e:
        return jsonify({"error": "Registration failed due to a database constraint"}), 500
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred during registration"}), 500






def login():
    return jsonify({"message": "Login successful!", "token": "example_token"}), 200

def logout():
    return jsonify({"message": "Logout successful!"}), 200