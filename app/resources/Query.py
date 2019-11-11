from flask_restful import Resource
from flask import request, jsonify
# from app.extensions import feedback, parqr, logger, schema
from app.exception import verify_non_empty_json_request
# from collections import defaultdict
import json
import boto3

lambda_client = boto3.client('lambda')
with open('related_courses.json') as f:
    related_courses = json.load(f)


class Query(Resource):

    # @schema.validate(query)
    @verify_non_empty_json_request
    def post(self):
        """
        Given course_id and query, retrieve 5 similar posts
        :return:
        """
        course_id = request.json['course_id']
        # if not Course.objects(course_id=course_id):
        #     print('New un-registered course found: {}'.format(course_id))
        #     return {'message': "Course with course id {} not supported at this "
        #                        "time.".format(course_id)}, 400

        query = request.json['query']
        print("Getting similar posts from course {} with query {}".format(course_id, query))
        payload = {
            "course_id": course_id,
            "query": query,
            "N": 5
        }
        print(payload)
        response = lambda_client.invoke(
            FunctionName='Parqr',
            InvocationType='RequestResponse',
            Payload=bytes(json.dumps(payload), encoding='utf8')
        )
        similar_posts = json.loads(response['Payload'].read().decode("utf-8"))

        # if feedback.requires_feedback():
        #     query_rec_id = feedback.save_query_rec_pair(course_id, query, similar_posts)
        #     similar_posts = feedback.update_recommendations(query_rec_id, similar_posts)

        return similar_posts


# class Instructor_Query(Resource):
#
#     @verify_non_empty_json_request
#     # @schema.validate(query)
#     def post(self):
#         course_id = request.args.get('course_id')
#         if not Course.objects(course_id=course_id) or course_id not in related_courses:
#             print('New un-registered course found: {}'.format(course_id))
#             return {'message': "Course with course id {} not supported at this "
#                                "time.".format(course_id)}, 400
#
#         query = request.args.get('query')
#
#         response = defaultdict(list)
#         for rel_course_id in related_courses[course_id]:
#             if not Course.objects(course_id=rel_course_id):
#                 continue
#
#             recs = parqr.get_recommendations(rel_course_id, query, 5)
#             recs_post_ids = [rec['pid'] for rec in recs.values()]
#             recommended_posts = Post.objects(course_id=rel_course_id,
#                                              post_id__in=recs_post_ids)
#
#             for post in recommended_posts:
#                 if post.i_answer is not None:
#                     response[rel_course_id].append({
#                         "post_id": post.post_id,
#                         "student_subject": post.subject,
#                         "student_post": post.body,
#                         "instructor_answer": post.i_answer
#                     })
#
#         return response
