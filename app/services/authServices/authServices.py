from flask import jsonify, request, current_app

def register():
    return jsonify({"message": "User registered successfully!"}), 201

def login():
    return jsonify({"message": "Login successful!", "token": "example_token"}), 200