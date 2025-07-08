import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "oracle+cx_oracle://skalarr:sifra123@host.docker.internal:1521/?service_name=xepdb1")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
