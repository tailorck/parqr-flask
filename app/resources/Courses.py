from flask_restful import Resource
from flask_jwt import jwt_required
from datetime import timedelta
from flask import request, jsonify
from app.tasksrq import parse_and_train_models
from datetime import datetime
from app.constants import (
    COURSE_PARSE_TRAIN_TIMEOUT_S,
    COURSE_PARSE_TRAIN_INTERVAL_S
)
from app.statistics import (
    get_unique_users,
    number_posts_prevented,
    total_posts_in_course
)
import logging
from app.extensions import scheduler, logger, schema, redis, parser
from app.exception import verify_non_empty_json_request
from app.schemas import course
from app.models.Course import Course
from app.statistics import is_course_id_valid

from marshmallow import Schema, fields, ValidationError


class courseSchema(Schema):
    cid = fields.Str(required=True)


class Courses(Resource):

    @jwt_required()
    def get(self, course_id):
        courses = parser.get_enrolled_courses()
        for c in courses:
            if c['course_id'] == course_id:
                logger.info(c)
                response = jsonify(c)
                response.status_code = 200
                return response

        return {'message': 'course not active'}, 400

class Actives(Resource):

    # @schema.validate(course)
    # @verify_non_empty_json_request
    @jwt_required()
    def post(self, course_id):
        '''
        insturctor registers the class
        :return:
        '''
        # try:
        #     res = courseSchema().load(course_id)
        # except ValidationError as err:
        #     return {'message': 'invalid input, object invalid'}, 400
        logging.info("course_id")

        if not redis.exists(course_id):
            logging.info('Registering new course: {}'.format(course_id))
            curr_time = datetime.now()
            delayed_time = curr_time + timedelta(minutes=5)

            new_course_job = scheduler.schedule(scheduled_time=datetime.now(),
                                                func=parse_and_train_models,
                                                kwargs={"course_id": course_id},
                                                interval=COURSE_PARSE_TRAIN_INTERVAL_S,
                                                timeout=COURSE_PARSE_TRAIN_TIMEOUT_S)
            redis.set(course_id, new_course_job.id)
            return {'message': 'class registered'}, 201
        else:
            # raise InvalidUsage('Course ID already exists', 400)
            return {'message': 'course already registered'}, 409

    # @schema.validate(course)
    # @verify_non_empty_json_request
    @jwt_required()
    def delete(self, course_id):
        try:
            res = courseSchema().load({'cid': course_id})
        except ValidationError as err:
            return {'message': 'invalid input, object invalid'}, 400

        if redis.exists(course_id):
            logger.info('Deregistering course: {}'.format(course_id))
            job_id_str = redis.get(course_id)
            scheduler.cancel(job_id_str)
            redis.delete(course_id)
            return {'course_id': course_id}, 201
        else:
            # raise InvalidUsage('Course ID does not exists', 400)
            return {'message': 'Course ID does not exists'}, 409


class Courses_Stat(Resource):

    @jwt_required()
    def get(self, course_id):
        '''
        Get num of unique users, num of post prevented, percent of Traffic reduced
        get_parqr_stats
        :param course_id:
        :return:
        '''

        try:
            start_time = int(request.args.get('start_time'))
        except (ValueError, TypeError) as e:
            return {'message': 'Invalid start time specified'}, 400
        num_active_uid = get_unique_users(course_id, start_time)
        num_post_prevented, posts_by_parqr_users = number_posts_prevented(course_id, start_time)
        num_total_posts = total_posts_in_course(course_id)
        num_all_post = float(posts_by_parqr_users + num_post_prevented)
        percent_traffic_reduced = (num_post_prevented / num_all_post) * 100
        return {'usingParqr': num_active_uid,
                'assistedCount': num_post_prevented,
                'percentTrafficReduced': percent_traffic_reduced}, 202


# class Courses_Enrolled(Resource):
#
#     @jwt_required()
#     def get(self):
#         return parser.get_enrolled_courses()


class Courses_Supported(Resource):

    @jwt_required()
    def get(self):
        '''
        If active, return courses_enrolled.
        Else, return courses supported.
        :return:
        '''
        args = request.args
        if bool(args['active']):
            return jsonify(Course.objects.values_list('cid'))
        else:
            return parser.get_enrolled_courses()


class Courses_Valid(Resource):

    def get(self):
        # course_id = request.args.get('course_id')
        course_id = request.json['course_id']
        is_valid = is_course_id_valid(course_id)
        return {'valid': is_valid}, 202