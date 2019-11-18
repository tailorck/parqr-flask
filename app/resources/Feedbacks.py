from flask_restful import Resource
from flask import request, jsonify
from app.exception import InvalidUsage
from app.extensions import feedback, schema
from app.feedback import Feedback
from app.resources import feedback_schema
from app.exception import verify_non_empty_json_request
from app.schemas import feedback_schema
from marshmallow import Schema, fields, ValidationError

class feedbacksSchema(Schema):
    course_id = fields.Str(required=True)
    user_id = fields.Str(required=True)
    query_recommendation_id = fields.Str(required=True)
    feedback_pid = fields.Integer(required=True)
    user_rating = fields.Integer(required=True)


class Feedbacks(Resource):

    @verify_non_empty_json_request
    # @schema.validate(feedback_schema)
    def post(self):
        # Validate the feedback data
        try:
            res = feedbacksSchema().load(request.get_json())
        except ValidationError as err:
            return {'message': 'not valid schema'}, 202

        course_id, user_id, query_rec_id, feedback_pid, user_rating = Feedback.unpack_feedback(request.json)
        valid, message = feedback.validate_feedback(course_id, user_id, query_rec_id, feedback_pid, user_rating)

        # If not failed, return invalid usage
        if not valid:
            return {'message': "Feedback contains invalid data." + message}, 400
        success = Feedback.register_feedback(course_id, user_id, query_rec_id, feedback_pid, user_rating)

        if success:
            return {'message': 'success'}, 200

        else:
            return {'message': 'failure'}, 500
