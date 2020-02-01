from flask_restful import Resource, request


class Event(Resource):

    def post(self):
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
