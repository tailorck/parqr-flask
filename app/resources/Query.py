from flask_restful import Resource
from app.models.Course import Course
from flask import request, jsonify
from app.exception import InvalidUsage
from app.extensions import feedback, parqr, logger, schema
from app.resources import query


class Query(Resource):

    # @schema.validate(query)
    def post(self):
        '''
        Given course_id and query, retrieve 5 similar posts
        :return:
        '''
        course_id = request.json['course_id']
        if not Course.objects(course_id=course_id):
            logger.error('New un-registered course found: {}'.format(course_id))
            return {'message': "Course with course id {} not supported at this "
                               "time.".format(course_id)}, 400

        query = request.json['query']
        similar_posts = parqr.get_recommendations(course_id, query, 5)
        similar_posts = feedback.request_feedback(similar_posts)

        return similar_posts