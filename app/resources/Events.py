from flask_restful import Resource
from app.models.Event import Event
# from app.models.EventData import EventData
from flask import request, jsonify
from datetime import datetime
from app.extensions import logger, schema
from app.exception import verify_non_empty_json_request
from app.schemas import event
from marshmallow import Schema, fields, ValidationError


class eventsSchema(Schema):
    event_type = fields.Str(required=True)
    event_name = fields.Str(required=True)
    time = fields.Integer(required=True)
    user_id = fields.Str(required=True)
    course_id = fields.Str(required=True)
    event_data = fields.Dict(required=True)


class Events(Resource):

    @verify_non_empty_json_request
    # @schema.validate(event)
    def post(self):
        try:
            res = eventsSchema().load(request.get_json())
        except ValidationError as err:
            logger.info(err)
            return {'message': 'invalid input, object invalid'}, 400

        millis_since_epoch = request.json['time'] / 1000.0
        event = Event()
        event.event_type = request.json['event_type']
        event.event_name = request.json['event_name']
        event.time = datetime.fromtimestamp(millis_since_epoch)
        event.user_id = request.json['user_id']
        event.event_data = request.json['event_data']
        event.course_id = request.json['course_id']

        event.save()
        logger.info('Recorded {} event from cid {}'
                    .format(event.event_name, event.event_data['course_id']))

        return {'message': 'success'}, 200

