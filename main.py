
from flask_socketio import SocketIO
from flask import Flask
from database.config import Config
from database.dbClient import DatabaseClient
import jwt
from flask_jwt_extended import JWTManager
from app.utils import send_email
from flask_cors import CORS
from flask import send_from_directory

socketio = SocketIO(cors_allowed_origins="*")

from app.routes import (
    admin_routes,
    notification_routes,
    post_routes,
    user_profile_routes,
    auth_routes,
    friends_routes,
    search_routes
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your_secret_key'
    socketio.init_app(app)
    
 


    

# JWT konfiguracija
    app.config['JWT_SECRET_KEY'] = 'nas_secret_key_koji_bi_trebalo_da_se_nalazi_u_nekom_config_fileu'  # Zameni 'your_jwt_secret_key' pravim ključem
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Token će se tražiti u headerima
    app.config['JWT_HEADER_NAME'] = 'Authorization'  # Default je "Authorization"
    app.config['JWT_HEADER_TYPE'] = 'Bearer'  # Default je "Bearer"


    jwt = JWTManager(app)
    

    db_client = DatabaseClient(app)
    app.db_client = db_client

    # blueprintovi
    app.register_blueprint(admin_routes)
    app.register_blueprint(notification_routes)
    app.register_blueprint(user_profile_routes)
    app.register_blueprint(post_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(friends_routes)
    app.register_blueprint(search_routes)

    @socketio.on("connect")
    def handle_connect():
        print(f" Client connected ")

    @socketio.on("disconnect")
    def handle_disconnect():
        print(f" Client disconnected")

    @app.route('/')
    def home():
        return "Hello, Flask!"
    
    CORS(app)
    app.socketio = socketio
    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)

