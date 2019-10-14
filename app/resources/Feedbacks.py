from flask_restful import Resource
from flask import request, jsonify
from app.exception import InvalidUsage
from app.extensions import feedback, schema
from app.feedback import Feedback


class Feedbacks(Resource):

    @schema.validate('feedback')
    def post(self):
        # Validate the feedback data
        course_id, user_id, query_rec_id, feedback_pid, user_rating = Feedback.unpack_feedback(request.json)
        valid, message = feedback.validate_feedback(course_id, user_id, query_rec_id, feedback_pid, user_rating)

        # If not failed, return invalid usage
        if not valid:
            raise InvalidUsage("Feedback contains invalid data. " + message, 400)

        success = Feedback.register_feedback(course_id, user_id, query_rec_id, feedback_pid, user_rating)

        if success:
            return jsonify({'message': 'success'}), 200

        else:
            return jsonify({'message': 'failure'}), 500
