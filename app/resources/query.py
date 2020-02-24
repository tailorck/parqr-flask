from flask_restful import Resource
from flask import request
from collections import defaultdict
import json
import boto3

from app.extensions import feedback


def get_boto3_lambda():
    return boto3.client('lambda')


# with open('../related_courses.json') as f:
#     related_courses = json.load(f)


class StudentQuery(Resource):

    def post(self, course_id):
        """
        Given course_id and query, retrieve 5 similar posts
        :return:
        """
        query = request.json['query']
        if query is None:
            return {'message': 'invalid input, object invalid'}, 400

        print("Getting similar posts from course {} with query {}".format(course_id, query))
        payload = {
            "course_id": course_id,
            "query": query,
            "N": 5
        }
        print(payload)
        lambda_client = get_boto3_lambda()
        response = lambda_client.invoke(
            FunctionName='Parqr',
            InvocationType='RequestResponse',
            Payload=bytes(json.dumps(payload), encoding='utf8')
        )
        similar_posts = json.loads(response['Payload'].read().decode("utf-8"))

        # feedback_payload = {
        #     "source": "query",
        #     "course_id": course_id,
        #     "query": query,
        #     "similar_posts": similar_posts
        # }
        #
        # response = lambda_client.invoke(
        #     FunctionName='Feedbacks',
        #     InvocationType='RequestResponse',
        #     Payload=bytes(json.dumps(feedback_payload), encoding='utf8')
        # )
        # similar_posts = json.loads(response['Payload'].read().decode("utf-8")).get("similar_posts")

        return similar_posts, 200


class InstructorQuery(Resource):

    # TODO: FIX this
    def post(self, course_id):
        # if not Course.objects(course_id=course_id) or course_id not in related_courses:
        #     logger.error('New un-registered course found: {}'.format(course_id))
        #     return {'message': "Course with course id {} not supported at this "
        #                        "time.".format(course_id)}, 400

        query = request.json['query']

        response = defaultdict(list)
        # for rel_course_id in related_courses[course_id]:
        #     if not Course.objects(course_id=rel_course_id):
        #         continue
        #
        #     TODO: Get recommendations from parqr service
        #     recs = parqr.get_recommendations(rel_course_id, query, 5)
        #     recs_post_ids = [rec['pid'] for rec in recs.values()]
        #     recommended_posts = Post.objects(course_id=rel_course_id,
        #                                      post_id__in=recs_post_ids)
        #
        #     for post in recommended_posts:
        #         if post.i_answer is not None:
        #             response[rel_course_id].append({
        #                 "post_id": post.post_id,
        #                 "student_subject": post.subject,
        #                 "student_post": post.body,
        #                 "instructor_answer": post.i_answer
        #             })

        return response
