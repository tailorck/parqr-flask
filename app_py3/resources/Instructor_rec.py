from collections import defaultdict

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

from app_py3.extensions import related_courses


class Query(Resource):
    decorators = [validate('query'), verify_non_empty_json_request]


    def post(self):
        '''
        Given course_id and query, get related course_ids, get 5 similar posts.


        :return:
        '''
        course_id = request.json['course_id']
        if not Course.objects(course_id=course_id) or course_id not in related_courses:
            logging.error('New un-registered course found: {}'.format(course_id))
            raise InvalidUsage("Course with course id {} not supported at this "
                               "time.".format(course_id), 400)

        query = request.json['query']

        response = defaultdict(list)
        for rel_course_id in related_courses[course_id]:
            if not Course.objects(course_id=rel_course_id):
                continue

            recs = parqr.get_recommendations(rel_course_id, query, 5)
            recs_post_ids = [rec['pid'] for rec in recs.values()]
            recommended_posts = Post.objects(course_id=rel_course_id,
                                             post_id__in=recs_post_ids)

            for post in recommended_posts:
                if post.i_answer is not None:
                    response[rel_course_id].append({
                        "post_id": post.post_id,
                        "student_subject": post.subject,
                        "student_post": post.body,
                        "instructor_answer": post.i_answer
                    })

        return jsonify(response)