from flask_restful import Resource
from app.models.Course import Course
from flask import jsonify
from flask_jwt import jwt_required


class Course_Supported(Resource):

    # @jwt_required()
    def get(self):
        return Course.objects.values_list('course_id')

