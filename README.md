# DRS_projekat
Drustvena mreza

# Folder-file struktura
Ovaj deo je citljiv unutar Visual Studio Code-a
Po potrebiti dodati nove foldere i file-ove
Folder-file arhitektura:
/project-root
  /app                  # Glavni folder za Flask aplikaciju
    /templates          # HTML fajlovi (Jinja2 templati)
    /static             # CSS, JavaScript, slike
      /css
      /js
      /images
    __init__.py         # Flask instanca
    routes.py           # Definicija ruta
    models.py           # SQLAlchemy modeli (ako koristimo SQL bazu)
    forms.py            # Flask-WTF forme (ako budemo koristili)
  /engine               # Folder za API logiku
    __init__.py         # Inicijalizacija engine modula
    api.py              # API endpointi
    auth.py             # Endpoint za autentifikaciju
    friends.py          # Endpoint za prijatelje
    search.py           # Endpoint za pretragu

  /db                   # Folder za baze podataka, Potencijalan folder koji je visak
    migrations          # (npr. za SQLAlchemy migracije)
  /database
    01_create_tables.sql
    02_seed_data.sql
    03_indexes.sql
  .env                  # Potrebno za Docker Image
  config.py             # Konfiguracija aplikacije (dev/prod)
  requirements.txt      # Python dependency-i
  .gitignore            # Ignorisanje nepotrebnih fajlova
  app.py                # Ulazna tačka aplikacije

