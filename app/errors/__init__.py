from flask import Blueprint

'''
Creation of blueprint for errors

The Blueprint class takes the name of the blueprint, 
the name of the base module (typically set to __name__), 
and a few optional arguments, which in this case I do not need. 

After the blueprint object is created, I import the handlers.py module, 
so that the error handlers in it are registered with the blueprint. 

This import is at the bottom to avoid circular dependencies.
'''

bp = Blueprint('errors', __name__)
from app.errors import handlers