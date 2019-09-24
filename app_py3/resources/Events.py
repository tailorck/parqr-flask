from flask_restful import Resource
from app import app
from flask import request, jsonify
from flask_jsonschema import JsonSchema, JsonValidationError, validate

from datetime import datetime
from flask_mongoengine import MongoEngine
from app_py3.models import EventData
import logging
from passlib.apps import custom_app_context as pwd_context
from app_py3.common import verify_non_empty_json_request
from app_py3.models import Course, Event, EventData, User, Post

class Event(Resource):
    #decorator
    decorators = [validate('event'), verify_non_empty_json_request]

    def __init__(self):
        pass

    def get(self):
        pass

    def post(self):
        '''
        Register Event
        :return:
        '''
        millis_since_epoch = request.json['time'] / 1000.0

        event = Event()
        event.event_type = request.json['type']
        event.event_name = request.json['eventName']
        event.time = datetime.fromtimestamp(millis_since_epoch)
        event.user_id = request.json['user_id']
        event.event_data = EventData(**request.json['eventData'])

        event.save()
        logging.info('Recorded {} event from cid {}'
                    .format(event.event_name, event.event_data.course_id))

        return {'message': 'success'}, 200