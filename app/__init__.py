from flask import Flask, url_for
import os
from .models import db
from .routes_main import routes_main

app = Flask(__name__)

# Configuración
SECRET_KEY = "muydificil"
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database.db')

with app.app_context():
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')

db.init_app(app)
app.register_blueprint(routes_main)
