#app and routes
from flask import Flask, jsonify, make_response, request, current_app
from flask_jsonschema import JsonSchema, ValidationError

from app_py3 import auth, resources
#complete import statements
from app_py3.extensions import db, jwt, redis, parqr, redis_host


from app_py3.resources.Course import Course


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'endpoint not found'}), 404)


@app.errorhandler(InvalidUsage)
def on_invalid_usage(error):
    return make_response(jsonify(to_dict(error)), error.status_code)


@app.errorhandler(ValidationError)
def on_validation_error(error):
    return make_response(jsonify(to_dict(error)), 400)

api.add_resource(Course, '/Course', '/Course/<str:id>')
api.add_resource(Course, '/Course', '/Course/<str:id>')
api.add_resource(Course, '/Course', '/Course/<str:id>')
api.add_resource(Course, '/Course', '/Course/<str:id>')

if __name__ == '__main__':
    app.run(debug=True)