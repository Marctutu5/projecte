from flask import Flask
import os
from models import db
from routes_main import routes_main

app = Flask(__name__)

# Configuración
SECRET_KEY = "muydificil"
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath('db/database.db')

db.init_app(app)
app.register_blueprint(routes_main)

if __name__ == '__main__':
    app.run(debug=True)
