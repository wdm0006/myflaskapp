# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, render_template
from flask.ext.heroku import Heroku
import logging
import sys
import os
from myflaskapp.settings import ProdConfig
from myflaskapp.assets import assets
from myflaskapp.extensions import (
    bcrypt,
    cache,
    db,
    login_manager,
    mail,
    migrate,
    debug_toolbar,
)
from myflaskapp.views import public, user, blog, admin


def create_app(config_object=ProdConfig):
    """An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    app.config.from_object(config_object)

    if config_object == ProdConfig:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    assets.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    return None


def register_blueprints(app):
    app.register_blueprint(public.blueprint)
    app.register_blueprint(user.blueprint)
    app.register_blueprint(blog.blueprint)
    app.register_blueprint(admin.blueprint)
    return None


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None
