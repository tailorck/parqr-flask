from flask import Blueprint

'''
Creation of blueprint for authentication
'''

bp = Blueprint('auth', __name__)
from app.auth import routes