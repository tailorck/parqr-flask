from flask_restful import Resource
from app import app
from flask import request, jsonify
from flask_jsonschema import JsonSchema, ValidationError, validate

from datetime import datetime
from flask_mongoengine import MongoEngine
from app_py3.models import EventData
import logging
from passlib.apps import custom_app_context as pwd_context
from app_py3.common import verify_non_empty_json_request, InvalidUsage
from app_py3.models import Course, Event, EventData, User, Post
from app_py3 import parqr

class Query(Resource):
    #decorator
    decorators = [validate('query'), verify_non_empty_json_request]

    def __init__(self):
        pass

    def get(self):
        pass

    def post(self):
        '''
        Given course_id and query, retrieve 5 similar posts
        :return:
        '''
        course_id = request.json['course_id']
        if not Course.objects(course_id=course_id):
            logging.error('New un-registered course found: {}'.format(course_id))
            raise InvalidUsage("Course with course id {} not supported at this "
                               "time.".format(course_id), 400)

        query = request.json['query']
        similar_posts = parqr.get_recommendations(course_id, query, 5)
        return jsonify(similar_posts)