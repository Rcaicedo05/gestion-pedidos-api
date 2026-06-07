from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        db.create_all(checkfirst=True)

    from app.routes import orders_bp
    app.register_blueprint(orders_bp, url_prefix='/api')

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    return app
