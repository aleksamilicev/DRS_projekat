from flask import Flask
from database.config import Config
from database.dbClient import DatabaseClient

def create_app():
    # Create and configure the Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize the database client
    db_client = DatabaseClient(app)

    # Register routes
    @app.route('/')
    def home():
        return "Hello, Flask!"

   
    return app, db_client

# Main 
if __name__ == '__main__':
    app, db_client = create_app()  
    app.run(debug=True)
