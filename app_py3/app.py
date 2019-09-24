#app and routes
from datetime import datetime, timedelta
from collections import namedtuple, defaultdict
import logging
import json

from flask import jsonify, make_response, request, current_app, Blueprint
from flask_jsonschema import JsonSchema, ValidationError, validate
from flask_httpauth import HTTPBasicAuth
from flask_jwt import JWT, jwt_required
from redis import Redis
from rq_scheduler import Scheduler
from flask_cors import CORS, cross_origin

from app_py3.models import Course, Event, EventData, User, Post
from app_py3.common.statistics import (
    get_unique_users,
    number_posts_prevented,
    total_posts_in_course,
    get_inst_att_needed_posts,
    get_stud_att_needed_posts,
    is_course_id_valid
)
from app_py3.constants import (
    COURSE_PARSE_TRAIN_TIMEOUT_S,
    COURSE_PARSE_TRAIN_INTERVAL_S
)

from app_py3.tasksrq import parse_and_train_models
from app_py3.common.utils import InvalidUsage, to_dict
from app_py3.parser import Parser
from app_py3.parqr import Parqr

from app_py3 import auth, resources
#complete import statements
from app_py3.extensions import db, jwt, redis, parqr, redis_host
from app_py3.resources.Course import Course

from app_py3 import app

#    decorators = [auth.login_required]


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'endpoint not found'}), 404)


@app.errorhandler(InvalidUsage)
def on_invalid_usage(error):
    return make_response(jsonify(to_dict(error)), error.status_code)


@app.errorhandler(ValidationError)
def on_validation_error(error):
    return make_response(jsonify(to_dict(error)), 400)


if __name__ == '__main__':
    app.run(debug=True)