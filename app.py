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

    # Return both the app and the db_client
    return app, db_client

# Main entry point
if __name__ == '__main__':
    app, db_client = create_app()  # Use the create_app function to initialize the app
    print("AAAAAAAAAAAAa")
    try:
        users = db_client.execute_query("SELECT * FROM licni_podaci_korisnika")
        print("Users:", users)
    except Exception as e:
        print("Error during query execution:", e)
    app.run(debug=True)
