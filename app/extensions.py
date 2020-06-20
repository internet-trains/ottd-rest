from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

def register_models():
    from app.models.company import Company
    from app.models.vehicle import Vehicle

def init_extensions(app):
    db.init_app(app)
    register_models()
    ma.init_app(app)
    migrate.init_app(app, db)
