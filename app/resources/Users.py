from flask_restful import Resource
from flask import request, jsonify
from app.exception import InvalidUsage
from app.extensions import schema
from app.models.User import User


class Users(Resource):

    @schema.validate('user')
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        if User.objects(username=username).first() is not None:
            raise InvalidUsage('Username already enrolled', 400)

        user = User(username=username)
        user.hash_password(password)
        user.save()
        return jsonify({'username': user.username}), 201