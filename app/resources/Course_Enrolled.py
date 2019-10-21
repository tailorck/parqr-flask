from flask_restful import Resource
from flask import jsonify
from flask_jwt import jwt_required
from app.extensions import parser


class Course_Enrolled(Resource):

    @jwt_required()
    def get(self):
        return parser.get_enrolled_courses()
