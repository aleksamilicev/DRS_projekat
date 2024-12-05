from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  

db = SQLAlchemy()

class DatabaseClient:
    def __init__(self, app):
        """
        Initialize SQLAlchemy with the Flask app.
        """
        db.init_app(app)
        self.app = app

    def execute_query(self, sql, params=None):
        """
        Executes a SELECT SQL query and returns results.
        :param sql: SQL query as a string.
        :param params: Parameters for the query (list or tuple).
        :return: List of results.
        """
        with self.app.app_context():
            # Wrap the query with `text()` if it's a raw SQL query
            result = db.session.execute(text(sql), params or {})
            return result.fetchall()
        
    def begin(self):
        """
        Start a transaction in SQLAlchemy.
        """
        db.session.begin()  # Begin a new transaction

    def commit(self):
        """
        Commit the current transaction.
        """
        db.session.commit()

    def rollback(self):
        """
        Rollback the current transaction in case of error.
        """
        db.session.rollback()
