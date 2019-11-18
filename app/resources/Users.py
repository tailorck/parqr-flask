from flask_restful import Resource
from flask import request, jsonify
from app.exception import InvalidUsage
from app.extensions import schema
from app.models.User import User
from app.exception import verify_non_empty_json_request
from app.schemas import user
from marshmallow import Schema, fields, ValidationError

class userSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class Users(Resource):

    @verify_non_empty_json_request
    # @schema.validate(user)
    def post(self):
        try:
            res = userSchema().load(request.get_json())
        except ValidationError as err:
            return {'message': 'not valid schema'}, 202

        username = request.json.get('username')
        password = request.json.get('password')

        if User.objects(username=username).first() is not None:
            return {'message': 'Username already enrolled'}, 400

        user = User(username=username)
        user.hash_password(password)
        user.save()
        return {'username': user.username}, 201
