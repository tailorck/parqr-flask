from flask_restful import Resource
from app import app
from flask import request, jsonify
from datetime import datetime
from flask_mongoengine import MongoEngine
from passlib.apps import custom_app_context as pwd_context

db = MongoEngine(app)

class Event(Resource):
    #decorator
    decorators = [auth.login_required]

    def __init__(self):
        self.event_type = db.StringField(required=True)
        self.event_name = db.StringField(required=True)
        self.time = db.DateTimeField(required=True)
        self.user_id = db.StringField(required=True)
        self.event_data = db.EmbeddedDocumentField(EventData, default=EventData,
                                              required=True)

    def get(self):
        pass

    def post(self):
        millis_since_epoch = request.json['time'] / 1000.0

        event = Event()
        event.event_type = request.json['type']
        event.event_name = request.json['eventName']
        event.time = datetime.fromtimestamp(millis_since_epoch)
        event.user_id = request.json['user_id']
        event.event_data = EventData(**request.json['eventData'])

        event.save()
        logger.info('Recorded {} event from cid {}'
                    .format(event.event_name, event.event_data.course_id))

        return {'message': 'success'}, 200