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
        

    def execute(self, sql, params=None):
        """
        Executes an SQL query and returns the result.
        :param sql: SQL query as a string.
        :param params: Parameters for the query (list or tuple).
        :return: List of results for SELECT, or None for non-SELECT queries.
        """
        with self.app.app_context():
            result = db.session.execute(text(sql), params or {})
            if sql.strip().upper().startswith("SELECT"):  # Only process results for SELECT queries
                return result.fetchall()
            else:
                db.session.commit()  # Commit if it's a DML statement (INSERT, UPDATE, DELETE)
                return None  # No result expected for non-SELECT queries
