from flask import Blueprint
from .auth import register, login, logout
from .friends import send_friend_request, get_friend_requests, accept_friend_request, reject_friend_request, get_friends, delete_friend
from .search import search_users

# Kreiranje Blueprint-a za API
api = Blueprint('api', __name__)

# *** AUTENTIFIKACIJA ***
# Ruta za registraciju korisnika
api.add_url_rule('/auth/register', view_func=register, methods=['POST'])

# Ruta za prijavu korisnika
api.add_url_rule('/auth/login', view_func=login, methods=['POST'])

# Ruta za odjavu korisnika
api.add_url_rule('/auth/logout', view_func=logout, methods=['POST'])


# *** PRIJATELJI ***
# Ruta za slanje zahteva za prijateljstvo
api.add_url_rule('/friends/<int:user_id>/request', view_func=send_friend_request, methods=['POST'])

# Ruta za pregled zahteva za prijateljstvo
api.add_url_rule('/friends/requests', view_func=get_friend_requests, methods=['GET'])

# Ruta za prihvatanje zahteva za prijateljstvo
api.add_url_rule('/friends/<int:request_id>/accept', view_func=accept_friend_request, methods=['POST'])

# Ruta za odbijanje zahteva za prijateljstvo
api.add_url_rule('/friends/<int:request_id>/reject', view_func=reject_friend_request, methods=['POST'])

# Ruta za pregled liste prijatelja
api.add_url_rule('/friends', view_func=get_friends, methods=['GET'])

# Ruta za brisanje prijatelja
api.add_url_rule('/friends/<int:friend_id>', view_func=delete_friend, methods=['DELETE'])


# *** PRETRAGA ***
# Ruta za pretragu korisnika
api.add_url_rule('/search/users', view_func=search_users, methods=['GET'])
