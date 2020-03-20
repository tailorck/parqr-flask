from flask import jsonify, make_response, request
from flask_restful import Api, request, abort
from app.resources.course import (
    CoursesList,
    ActiveCourse,
    FindCourseByCourseID
)
from app.resources.event import Event
from app.resources.query import StudentQuery, InstructorQuery
from app.resources.recommendations import StudentRecommendations, InstructorRecommendations
from app.resources.user import Users
from app.resources.feedback import Feedbacks
from app.utils import create_app
from app.exception import InvalidUsage, to_dict
import awsgi


class CustomApi(Api):

    def handle_error(self, e):
        abort(e.code, str(e))


app = create_app("parqr")
api = CustomApi(app)

api.add_resource(CoursesList, '/courses')
api.add_resource(FindCourseByCourseID, '/course/<string:course_id>')
api.add_resource(ActiveCourse, '/course/<string:course_id>/active')

api.add_resource(StudentQuery, '/course/<string:course_id>/query/student')
api.add_resource(InstructorQuery, '/course/<string:course_id>/query/instructor')

api.add_resource(StudentRecommendations, '/courses/<string:course_id>/recommendation/student')
api.add_resource(InstructorRecommendations, '/courses/<string:course_id>/recommendation/instructor')

api.add_resource(Event, '/event')
api.add_resource(Feedbacks, '/feedback')

api.add_resource(Users, '/users')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'endpoint not found'}), 404)


@app.errorhandler(InvalidUsage)
def on_invalid_usage(error):
    return make_response(jsonify(to_dict(error)), error.status_code)


@app.route("/", methods=['GET', 'POST'])
def index():
    print(request.args.get('hi'))
    return "Hello, World!"


def lambda_handler(event, context):
    print(event, context)
    response = awsgi.response(app, event, context)
    print(response)
    return response
