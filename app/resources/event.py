from flask_restful import Resource, request


class Event(Resource):

    def post(self):
        event = request.json.get("event_type")
        user_id = request.json.get("user_id")
        course_id = request.json.get("course_id")
        event_data = request.json.get("event_data")

        print("Event {} happened with user_id {} in course_id {} with event_data {}".format(
            event, user_id, course_id, event_data
        ))

        return {'message': 'success'}, 200
