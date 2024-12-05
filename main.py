from flask import Flask
from database.config import Config
from database.dbClient import DatabaseClient
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

    
    db_client = DatabaseClient(app)
    
    # Attach db_client to the app
    app.db_client = db_client

    # Register blueprints
    app.register_blueprint(admin_routes)
    app.register_blueprint(notification_routes)
    app.register_blueprint(user_profile_routes)
    app.register_blueprint(post_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(friends_routes)
    app.register_blueprint(search_routes)

    @app.route('/')
    def home():
        return "Hello, Flask!"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
