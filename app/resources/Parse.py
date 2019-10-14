from flask_restful import Resource
from flask_jwt import jwt_required
from flask import request, jsonify
import redis
from app.exception import InvalidUsage
from app.extensions import parser, logger, schema


class Parse(Resource):

    @schema.validate('course')
    @jwt_required()
    def post(self):
        '''
        Given course_id and query, retrieve 5 similar posts
        :return:
        '''
        course_id = request.json['course_id']
        if redis.exists(course_id):
            logger.info('Triggering parse for course id {}'.format(course_id))
            successful_parse = parser.update_posts(course_id)

            if successful_parse:
                return jsonify({'message': 'success'}), 200

            else:
                return jsonify({'message': 'failure'}), 500

        else:
            raise InvalidUsage('Course ID does not exists', 400)