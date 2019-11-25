from flask import jsonify, make_response, request
from flask_json_schema import JsonValidationError
from flask_restful import Api

#     Course_Stat,
#     Course_Enrolled,
#     Course_Supported,
#     Course_Valid

from app.exception import InvalidUsage, to_dict
from app.resources import (
    Query,
    Courses,
    Top_Post,
    Course_Enrolled
)
from app import app
import awsgi

api_endpoint = '/Parqr-API'
api = Api(app)

api.add_resource(Courses, api_endpoint + '/courses')
# api.add_resource(Course_Stat, api_endpoint + '/courses/<string:course_id>')
api.add_resource(Course_Enrolled, api_endpoint + '/courses/<string:course_id>/enrolled')
# api.add_resource(Course_Supported, api_endpoint + '/courses/<string:course_id>/supported')
# api.add_resource(Course_Valid, api_endpoint + '/courses/<string:course_id>/valid')
# api.add_resource(Events, api_endpoint + '/events')
# api.add_resource(Instructor_Query, api_endpoint + '/query/instructor')
api.add_resource(Query, api_endpoint + '/similar_posts')
api.add_resource(Top_Post, api_endpoint + '/top_post/<string:course_id>/<string:user>')
# api.add_resource(Users, api_endpoint + '/users')
# api.add_resource(Feedbacks, api_endpoint + '/feedbacks')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'endpoint not found'}), 404)


@app.errorhandler(InvalidUsage)
def on_invalid_usage(error):
    return make_response(jsonify(to_dict(error)), error.status_code)


@app.errorhandler(JsonValidationError)
def on_validation_error(error):
    return make_response(jsonify(to_dict(error)), 400)


@app.route(api_endpoint, methods=['GET', 'POST'])
def index():
    print(request.args.get('hi'))
    return "Hello, World!"


def lambda_handler(event, context):
    print(event, context)
    response = awsgi.response(app, event, context)
    print(response)
    return response
