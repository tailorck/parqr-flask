from flask_restful import Resource
from app.models.Course import Course
from flask import request, jsonify
from app.exception import InvalidUsage
from app.extensions import feedback, parqr, logger, schema
from app.exception import verify_non_empty_json_request
from app.schemas import query


class Query(Resource):

    @schema.validate(query)
    @verify_non_empty_json_request
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
        if feedback.requires_feedback():
            query_rec_id = feedback.save_query_rec_pair(course_id, query, similar_posts)
            similar_posts = feedback.update_recommendations(query_rec_id, similar_posts)

        return similar_posts