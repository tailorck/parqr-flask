from flask_restful import Resource
from collections import defaultdict
from flask import request, jsonify
from app.models.Course import Course
from app.models.Post import Post
from app.exception import InvalidUsage
from app.extensions import logger, schema, parqr
from app.exception import verify_non_empty_json_request
from app.schemas import query


import json

with open('related_courses.json') as f:
    related_courses = json.load(f)


class Instructor_Query(Resource):

    @verify_non_empty_json_request
    @schema.validate(query)
    def post(self):
        course_id = request.json['course_id']
        if not Course.objects(course_id=course_id) or course_id not in related_courses:
            logger.error('New un-registered course found: {}'.format(course_id))
            return {'message': "Course with course id {} not supported at this "
                               "time.".format(course_id)}, 400

        query = request.json['query']

        response = defaultdict(list)
        for rel_course_id in related_courses[course_id]:
            if not Course.objects(course_id=rel_course_id):
                continue

            recs = parqr.get_recommendations(rel_course_id, query, 5)
            recs_post_ids = [rec['pid'] for rec in recs.values()]
            recommended_posts = Post.objects(course_id=rel_course_id,
                                             post_id__in=recs_post_ids)

            for post in recommended_posts:
                if post.i_answer is not None:
                    response[rel_course_id].append({
                        "post_id": post.post_id,
                        "student_subject": post.subject,
                        "student_post": post.body,
                        "instructor_answer": post.i_answer
                    })

        return response