import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Crear la app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configurar la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bot.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Inicializar la app con la extensión
db.init_app(app)

with app.app_context():
    # Importar los modelos aquí para que las tablas se creen
    import models  # noqa: F401
    db.create_all()

# Importar rutas
from routes import *  # noqa: F401, E402

# El scheduler se inicializará cuando sea necesario, no al inicio
