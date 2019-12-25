from flask import jsonify, make_response, request
from flask_json_schema import JsonValidationError
from flask_restful import Api
from app.resources.Courses import (
    CoursesList,
    ActiveCourse,
)
from app.resources.Event import Event
from app.resources.Parse import Parse
from app.resources.Queries import Student_Queries, Instructor_Queries
from app.resources.Recommendations import StudentRecommendations, InstructorRecommendations
from app.resources.Users import Users
from app.resources.Feedback import Feedback
from app.exception import InvalidUsage, to_dict
from app import app

api_endpoint = '/api/v2.0'
api = Api(app)

api.add_resource(CoursesList, api_endpoint + '/courses')
api.add_resource(ActiveCourse, api_endpoint + '/course/<string:course_id>/active')

api.add_resource(Student_Queries, api_endpoint + '/course/<string:course_id>/query/student')
api.add_resource(Instructor_Queries, api_endpoint + '/course/<string:course_id>/query/instructor')

api.add_resource(StudentRecommendations, api_endpoint + '/course/<string:course_id>/recommendation/student')
api.add_resource(InstructorRecommendations, api_endpoint + '/course/<string:course_id>/recommendation/instructor')


api.add_resource(Event, api_endpoint + '/event')
api.add_resource(Feedback, api_endpoint + '/feedback')

api.add_resource(Users, api_endpoint + '/users')
api.add_resource(Parse, api_endpoint + '/parse')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'endpoint not found'}), 404)


@app.errorhandler(InvalidUsage)
def on_invalid_usage(error):
    return make_response(jsonify(to_dict(error)), error.status_code)


@app.errorhandler(JsonValidationError)
def on_validation_error(error):
    # return make_response(jsonify(to_dict(error)), 400)
    return jsonify({'error': error.message,
                    'errors': [validation_error.message for validation_error
                               in error.errors]})

@app.route('/')
def index():
    return "Hello, World!"
