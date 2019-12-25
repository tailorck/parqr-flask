from datetime import datetime
import logging

from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from flask import jsonify

from app.tasksrq import parse_and_train_models
from app.exception import verify_non_empty_json_request
from app.constants import (
    COURSE_PARSE_TRAIN_TIMEOUT_S,
    COURSE_PARSE_TRAIN_INTERVAL_S
)
from app.extensions import (
    scheduler,
    logger,
    redis,
    parser
)


def mark_active_courses(course_list):
    for course in course_list:
        course['active'] = redis.exists(course.get('course_id', None))

    return course_list


class CoursesList(Resource):

    @verify_non_empty_json_request
    @jwt_required()
    def get(self, active):
        parser = reqparse.RequestParser()
        parser.add_argument('active', type=bool)
        args = parser.parse_args()

        courses = parser.get_enrolled_courses()
        courses = mark_active_courses(courses)

        if args.active:
            courses = list(filter(lambda x: x['active'], courses))

        return jsonify(courses)


class ActiveCourse(Resource):

    @verify_non_empty_json_request
    @jwt_required()
    def get(self, course_id):
        courses = parser.get_enrolled_courses()
        courses = mark_active_courses(courses)
        courses = list(filter(lambda x: x['active'], courses))
        return jsonify(courses)

    @verify_non_empty_json_request
    @jwt_required()
    def post(self, course_id):
        """
        instructor registers the class
        :return:
        """
        if not redis.exists(course_id):
            logging.info('Registering new course: {}'.format(course_id))

            new_course_job = scheduler.schedule(scheduled_time=datetime.now(),
                                                func=parse_and_train_models,
                                                kwargs={"course_id": course_id},
                                                interval=COURSE_PARSE_TRAIN_INTERVAL_S,
                                                timeout=COURSE_PARSE_TRAIN_TIMEOUT_S)
            redis.set(course_id, new_course_job.id)
            return {'message': 'Course {} registered'.format(course_id)}, 201
        else:
            return {'message': 'Course {} already registered'.format(course_id)}, 409

    @verify_non_empty_json_request
    @jwt_required()
    def delete(self, course_id):
        if redis.exists(course_id):
            logger.info('Deregistering course: {}'.format(course_id))
            job_id_str = redis.get(course_id)
            scheduler.cancel(job_id_str)
            redis.delete(course_id)
            return {'message': 'Course {} deregistered'.format(course_id)}, 201
        else:
            return {'message': 'Course ID does not exists'}, 409

