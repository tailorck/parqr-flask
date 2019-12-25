from flask_restful import Resource
from flask import request
from app.statistics import (
    get_inst_att_needed_posts,
    get_stud_att_needed_posts
)
from app.extensions import logger


class StudentRecommendations(Resource):

    def get(self, course_id):
        try:
            num_posts = int(request.args.get('num_posts'))
        except (ValueError, TypeError) as e:
            return {'message': 'Invalid number of posts specified. '
                               'Please specify the number of posts you would like '
                               'as a GET parameter num_posts'}, 400
        logger.error('course id is : {}'.format(course_id))
        posts = get_stud_att_needed_posts(course_id, num_posts)
        return {'posts': posts}, 200


class InstructorRecommendations(Resource):

    def get(self, course_id):
        try:
            num_posts = int(request.args.get('num_posts'))
        except (ValueError, TypeError) as e:
            return {'message': 'Invalid number of posts specified. '
                               'Please specify the number of posts you would like '
                               'as a GET parameter num_posts'}, 400
        logger.error('course id is : {}'.format(course_id))
        posts = get_inst_att_needed_posts(course_id, num_posts)
        return {'posts': posts}, 200
