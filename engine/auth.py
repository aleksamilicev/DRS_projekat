# /engine/auth.py

from flask import jsonify

def register():
    return jsonify({"message": "User registered successfully!"}), 201

def login():
    return jsonify({"message": "Login successful!", "token": "example_token"}), 200

def logout():
    return jsonify({"message": "Logout successful!"}), 200
