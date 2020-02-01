from flask import Flask, request

from app.config import config_dict
from app.exception import InvalidUsage


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
    app = Flask("app")

    # Override some parameters of rq_dashboard config with app.config
    app.config.from_object(config_dict[config_name])

    return app


def read_credentials():
    """Method to read encrypted .login file for Piazza username and password"""
    return 'parqrdevteam@gmail.com', 'parqrproducers'


def verify_non_empty_json_request(func):
    def wrapper(*args, **kwargs):
        if request.get_data() == '':
            raise InvalidUsage('No request body provided', 400)
        if not request.json:
            raise InvalidUsage('Request body must be in JSON format', 400)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
