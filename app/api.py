from collections import namedtuple
from flask import jsonify, make_response, request
from flask_json_schema import JsonSchema, JsonValidationError
from flask_jwt import JWT
from flask_restful import Api
from app.resources.Course import Course
from app.resources.Course_Enrolled import Course_Enrolled
from app.resources.Course_Supported import Course_Supported
from app.resources.Course_Validator import Course_Validator
from app.resources.Events import Events
from app.resources.Instructor_Query import Instructor_Query
from app.resources.Parse import Parse
from app.resources.Query import Query
from app.resources.Top_Post import Top_Post
from app.resources.Users import Users
from app.resources.Feedbacks import Feedbacks


from app.models import User
from app.exception import InvalidUsage, to_dict
from app.parser import Parser
from app.parqr import Parqr
from app.extensions import jwt, redis, parqr, redis_host, scheduler
from app import app


api_endpoint = '/api/2.0'
api = Api(app)
api.add_resource(Course, api_endpoint + '/course/<string:course_id>')
api.add_resource(Course_Enrolled, api_endpoint + '/courses_enrolled')
api.add_resource(Course_Supported, api_endpoint + '/courses_supported')
api.add_resource(Course_Validator, api_endpoint + '/isvalid')
api.add_resource(Events, api_endpoint + '/events')
api.add_resource(Instructor_Query, api_endpoint + '/instructor_recommendations')
api.add_resource(Parse, api_endpoint + '/parse')
api.add_resource(Query, api_endpoint + '/similar_posts')
api.add_resource(Top_Post, api_endpoint + '/top_post/<string:course_id>/<string:user>')
api.add_resource(Users, api_endpoint + '/users')
api.add_resource(Feedbacks, api_endpoint + '/feedbacks')



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


