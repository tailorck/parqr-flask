'''
a set of helper functions to fulfill common needs across your application.
It could also contain any custom input/output types your resources need to get the job done.
'''
from flask import request, Flask
from logging.handlers import RotatingFileHandler
import logging
import os

from flask import Flask
import rq_dashboard
from Crypto.PublicKey import RSA
import Crypto
from ..extensions import db, jwt
from ..config import config_dict


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

def to_dict(exception):
    if hasattr(exception, 'payload') and exception.payload is not None:
        rv = dict(exception.payload)
    else:
        rv = dict()

    rv['message'] = exception.message
    return rv

def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/rq')

def create_app(config_name):
    """Creates a flask object with the appropriate configurations.

    Parameters
    ----------
    config_name : str
        config_name is a string to declare the type of configuration to put the
        application in. It is one of ['development', 'production', 'testing'].

    Returns
    -------
    app : Flask object
    """
    app = Flask(__name__)

    # First import the default settings from rq_dashboard to monitor redis
    # queues on the web.
    app.config.from_object(rq_dashboard.default_settings)
    register_blueprints(app)


    '''
    Import and register the blueprint from the factory using app.register_blueprint(). 
    Place the new code at the end of the factory function before returning the app.

    When a blueprint is registered, 
    any view functions, templates, static files, error handlers, etc. are connected to the app

    The error blueprint will have views to (functionality of app)
    '''
    # from app.errors import bp as errors_bp
    # app.register_blueprint(errors_bp)
    #
    # from app.auth import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    # Override some parameters of rq_dashboard config with app.config
    app.config.from_object(config_dict[config_name])

    if not os.path.isdir(app.config['LOG_FOLDER']):
        os.makedirs(app.config['LOG_FOLDER'])

    log_file = os.path.join(app.config['LOG_FOLDER'], 'app.log')
    log_level = app.config['LOG_LEVEL']
    fh = RotatingFileHandler(log_file, maxBytes=100 * 1024 * 1024, backupCount=5)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s '
                                  '%(module)s: %(message)s')
    app.logging.addHandler(fh)
    for handler in app.logging.handlers:
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
    app.logging.setLevel(log_level)

    return app


def configure_extensions(app, cli):
    """configure flask extensions
    """
    db.init_app(app)
    jwt.init_app(app)


def read_credentials():
    """Method to read encrypted .login file for Piazza username and password"""
    with open('.key.pem') as f:
        key = RSA.importKey(f.read())

    with open('.login') as f:
        email_bytes = f.read(128)
        password_bytes = f.read(128)

    return key.decrypt(email_bytes), key.decrypt(password_bytes)

def verify_non_empty_json_request(func):
    def wrapper(*args, **kwargs):
        if request.get_data() == '':
            raise InvalidUsage('No request body provided', 400)
        if not request.json:
            raise InvalidUsage('Request body must be in JSON format', 400)
        return func(*args, **kwargs)
    wrapper.func_name = func.func_name
    return wrapper