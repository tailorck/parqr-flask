from flask_restful import Resource
from flask import request
from app.models.user import User
from app.exception import verify_non_empty_json_request


class Users(Resource):

    @verify_non_empty_json_request
    # @schema.validate(user)
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        if User.objects(username=username).first() is not None:
            return {'message': 'Username already enrolled'}, 400

        user = User(username=username)
        user.hash_password(password)
        user.save()
        return {'username': user.username}, 201
