# config.py fajl se koristi za definisanje konfiguracija Flask aplikacije,
# kao što su tajni ključevi, baza podataka, debug mod i slične postavke

from dotenv import load_dotenv
import os

# Učitaj varijable iz .env fajla
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db') # Zameniti SQLite sa pravim DB URI ako koristimo neku drugu bazu
    DEBUG = True    # Postavi na False u produkciji
    TESTING = False

