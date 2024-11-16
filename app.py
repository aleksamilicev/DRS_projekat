from flask import Flask

app = Flask(__name__)

# Konfiguracija aplikacije
app.config['SECRET_KEY'] = 'your_secret_key'

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
