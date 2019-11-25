from flask_restful import Resource
# from flask_jwt import jwt_required
# from datetime import timedelta
from flask import request, jsonify
import json
import time
# from app.tasksrq import parse_and_train_models
# from datetime import datetime
# from app.constants import (
#     COURSE_PARSE_TRAIN_TIMEOUT_S,
#     COURSE_PARSE_TRAIN_INTERVAL_S
# )
import boto3
# from app.statistics import (
#     get_unique_users,
#     number_posts_prevented,
#     total_posts_in_course
# )
# import logging
# from app.extensions import scheduler, logger, schema, redis, parser
from app.exception import verify_non_empty_json_request


# from app.models.Course import Course
# from app.statistics import is_course_id_valid


class Courses(Resource):

    @verify_non_empty_json_request
    # @jwt_required()
    def post(self):
        """
        instructor registers the class
        :return:
        """
        try:
            cid = request.json['course_id']
        except KeyError as err:
            print(request)
            return {'message': 'not valid schema'}, 400
        print('Registering new course: {}'.format(cid))

        cloudwatch_events = boto3.client("events")
        rule_arn = cloudwatch_events.put_rule(
            Name=cid,
            ScheduleExpression='rate(15 minutes)',
            State='ENABLED'
        ).get('RuleArn')

        lambda_client = boto3.client('lambda')
        lambda_response = lambda_client.add_permission(
            FunctionName='Parser:PROD',
            StatementId=cid + str(int(time.time())),
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )

        lambda_arn = json.loads(lambda_response.get('Statement')).get('Resource')

        cloudwatch_events.put_targets(
            Rule=cid,
            Targets=[
                {
                    'Id': cid + str(int(time.time())),
                    'Arn': lambda_arn
                }
            ]
        )

        if lambda_response.get('Statement'):
            return {'course_id': cid}, 202
        else:
            print("Error registering course")
            print(lambda_response)
            return {'message': 'Internal Server Error'}, 500

    # @schema.validate(course)
    @verify_non_empty_json_request
    # @jwt_required()
    def delete(self):
        try:
            cid = request.json['course_id']
        except KeyError as err:
            print(request)
            return {'message': 'not valid schema'}
        print('Deregistering course: {}'.format(cid))

        cloudwatch_events = boto3.client("events")
        cloudwatch_events.disable_rule(
            Name=cid
        )

        return {'course_id': cid}, 200


# class Course_Stat(Resource):
#
#     @jwt_required()
#     def get(self, course_id):
#         '''
#         Get num of unique users, num of post prevented, percent of Traffic reduced
#         get_parqr_stats
#         :param course_id:
#         :return:
#         '''
#
#         try:
#             start_time = int(request.args.get('start_time'))
#         except (ValueError, TypeError) as e:
#             return {'message': 'Invalid start time specified'}, 400
#         num_active_uid = get_unique_users(course_id, start_time)
#         num_post_prevented, posts_by_parqr_users = number_posts_prevented(course_id, start_time)
#         num_total_posts = total_posts_in_course(course_id)
#         num_all_post = float(posts_by_parqr_users + num_post_prevented)
#         percent_traffic_reduced = (num_post_prevented / num_all_post) * 100
#         return {'usingParqr': num_active_uid,
#                 'assistedCount': num_post_prevented,
#                 'percentTrafficReduced': percent_traffic_reduced}, 202
#
#
class Course_Enrolled(Resource):

    # @jwt_required()
    def get(self, course_id):
        courses = boto3.resource("dynamodb").Table("Courses")
        exists = courses.get_item(
            Key={
                "course_id": course_id
            }
        ).get("Item")
        return True if exists is not None else False


# class Course_Supported(Resource):
#
#     @jwt_required()
#     def get(self):
#         return jsonify(Course.objects.values_list('course_id'))
#
#
# class Course_Valid(Resource):
#
#     def get(self):
#         # course_id = request.args.get('course_id')
#         course_id = request.json['course_id']
#         is_valid = is_course_id_valid(course_id)
#         return {'valid': is_valid}, 202
