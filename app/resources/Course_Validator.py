from flask_restful import Resource
from flask import request, jsonify
from app.statistics import is_course_id_valid


class Course_Validator(Resource):

    def get(self):
        course_id = request.args.get('course_id')
        is_valid = is_course_id_valid(course_id)
        return jsonify({'valid': is_valid}), 202

