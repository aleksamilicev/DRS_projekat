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
  /db                   # Folder za baze podataka
    migrations          # (npr. za SQLAlchemy migracije)
  config.py             # Konfiguracija aplikacije (dev/prod)
  requirements.txt      # Python dependency-i
  .gitignore            # Ignorisanje nepotrebnih fajlova
  app.py                # Ulazna tačka aplikacije

