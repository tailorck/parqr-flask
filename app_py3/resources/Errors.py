from flask_restful import Resource

class Course(Resource):
    def get(self):
        pass
    def post(self):
        pass

# @app.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify({'error': 'endpoint not found'}), 404)
#
#
# @app.errorhandler(InvalidUsage)
# def on_invalid_usage(error):
#     return make_response(jsonify(to_dict(error)), error.status_code)
#
#
# @app.errorhandler(ValidationError)
# def on_validation_error(error):
#     return make_response(jsonify(to_dict(error)), 400)