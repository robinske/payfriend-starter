import os
from config import config
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, g
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    load_dotenv(find_dotenv())
    config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # register the database
    from payfriend import models
    db.init_app(app)
    db.create_all(app=app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/users')
    def list_users():
        from payfriend.models import User
        users = User.query.all()
        return render_template('users.html', users=users)

    # apply the blueprints to the app
    from payfriend import auth, payment
    app.register_blueprint(payment.bp)
    app.register_blueprint(auth.bp)

    # add error routing
    from payfriend import error
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(403, error.forbidden)
    app.register_error_handler(404, error.page_not_found)
    app.register_error_handler(500, error.internal_error)

    return app


