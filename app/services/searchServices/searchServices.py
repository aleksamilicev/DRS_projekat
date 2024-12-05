from flask import jsonify, request, current_app

def search_users():
    email = request.args.get('email')
    username = request.args.get('username')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    city = request.args.get('city')
    
    query_params = {
        "email": email,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "city": city
    }
    return jsonify({"message": "Search results", "query": query_params}), 200