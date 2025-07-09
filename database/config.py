import os

class Config:
    # Format for connecting with SID instead of service_name
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "oracle+cx_oracle://admin:065235805Slavko@database-drs.cx8sygmoo3j3.eu-central-1.rds.amazonaws.com:1521/DATABASE"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
