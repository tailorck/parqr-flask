from flask_restful import Resource
from app import app
from datetime import timedelta
from flask import request, jsonify
from flask_jsonschema import JsonSchema, ValidationError, validate
from app_py3.extensions import scheduler
from app_py3.tasksrq import parse_and_train_models

import redis
from datetime import datetime
from app_py3.constants import (
    COURSE_PARSE_TRAIN_TIMEOUT_S,
    COURSE_PARSE_TRAIN_INTERVAL_S
)
from flask_mongoengine import MongoEngine
from app_py3.models import EventData
import logging
from passlib.apps import custom_app_context as pwd_context
from app_py3.common import verify_non_empty_json_request, InvalidUsage
from app_py3.models import Course, Event, EventData, User, Post

class Course(Resource):
    def get(self):
        pass

    def post(self):
        '''
            insturctor registers the class

            :return:
            '''
        cid = request.json['course_id']
        if not redis.exists(cid):
            logging.info('Registering new course: {}'.format(cid))
            curr_time = datetime.now()
            delayed_time = curr_time + timedelta(minutes=5)

            new_course_job = scheduler.schedule(scheduled_time=datetime.now(),
                                                func=parse_and_train_models,
                                                kwargs={"course_id": cid},
                                                interval=COURSE_PARSE_TRAIN_INTERVAL_S,
                                                timeout=COURSE_PARSE_TRAIN_TIMEOUT_S)
            redis.set(cid, new_course_job.id)
            return jsonify({'course_id': cid}), 202
        else:
            raise InvalidUsage('Course ID already exists', 400)