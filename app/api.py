from collections import namedtuple
import logging
import json

from flask import jsonify, make_response, request
from flask_json_schema import JsonSchema, JsonValidationError

from flask_httpauth import HTTPBasicAuth
from flask_jwt import JWT
from redis import Redis
from rq_scheduler import Scheduler
from flask_cors import CORS
from flask_restful import Api
from app.resources.Course import Course
from app.resources.Course import Course
from app.resources.Course import Course
from app.resources.Course import Course
from app.resources.Course import Course
from app.resources.Course import Course


from app import app

from app.models import User

from app.exception import InvalidUsage, to_dict
from app.parser import Parser
from app.parqr import Parqr

api_endpoint = '/api/'

parqr = Parqr()
parser = Parser()
schema = JsonSchema(app)

logger = logging.getLogger('app')

redis_host = app.config['REDIS_HOST']
redis_port = app.config['REDIS_PORT']
redis = Redis(host=redis_host, port=redis_port, db=0)
scheduler = Scheduler(connection=redis)
auth = HTTPBasicAuth()

logger.info('Ready to serve requests')

with open('related_courses.json') as f:
    related_courses = json.load(f)
CORS(app)
api = Api(app)

###########################################################################
def verify(username, password):
    Identity = namedtuple('Identity', ['id'])
    user = User.objects(username=username).first()
    if not user or not user.verify_password(password):
        return False
    return Identity(str(user.pk))


def identity(payload):
    user_id = payload['identity']
    return User.objects(pk=user_id).first()


jwt = JWT(app, verify, identity)

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')

###########################################################################

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'endpoint not found'}), 404)


@app.errorhandler(InvalidUsage)
def on_invalid_usage(error):
    return make_response(jsonify(to_dict(error)), error.status_code)


@app.errorhandler(JsonValidationError)
def on_validation_error(error):
    return make_response(jsonify(to_dict(error)), 400)


def verify_non_empty_json_request(func):
    def wrapper(*args, **kwargs):
        if request.get_data() == '':
            raise InvalidUsage('No request body provided', 400)
        if not request.json:
            raise InvalidUsage('Request body must be in JSON format', 400)
        return func(*args, **kwargs)
    wrapper.func_name = func.__name__
    return wrapper


@app.route('/')
def index():
    return "Hello, World!"


