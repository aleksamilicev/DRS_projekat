class Config:
    # Proper connection string with service name
    SQLALCHEMY_DATABASE_URI = (
        "oracle+cx_oracle://Slavko:ftn@localhost:1521/?service_name=xepdb1"
    )  
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Suppress warnings
    SQLALCHEMY_ECHO = False  # Optional: True to log SQL queries
