from app.parser import Parser
from flask import jsonify

class Event(Resource):

    @app.route('/api/enrolled_classes', methods=['GET'])
    @jwt_required()
    def get(self):
        enrolled_courses = self._piazza.get_user_classes()
        resp = [{'name': d['name'], 'course_id': d['nid'], 'term': d['term'],
                 'course_num': d['num']} for d in enrolled_courses]

        return jsonify(resp)

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

        return jsonify({'message': 'success'}), 200


