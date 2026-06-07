from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)

    # Configuración base
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/orders.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    ma.init_app(app)

    # Registro de las rutas (Blueprints)
    from app.routes import orders_bp
    app.register_blueprint(orders_bp, url_prefix='/api')

    return app
