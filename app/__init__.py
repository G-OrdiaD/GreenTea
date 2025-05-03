from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .utils.logger import setup_logger
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    app.config.from_object('config.Config')
    app.logger = setup_logger('greenhouse')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    from .routes import bp as main_bp
    from .auth import bp as auth_bp
    from .admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        from .utils.monitoring import insert_default_optimal_ranges
        insert_default_optimal_ranges()

    csrf.exempt(lambda request: request.method in {'GET', 'HEAD', 'OPTIONS', 'TRACE'})

    return app