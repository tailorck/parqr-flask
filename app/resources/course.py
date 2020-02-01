from flask_restful import Resource
# from flask_jwt import jwt_required
from flask import request
import json
import time
import boto3
from app.exception import verify_non_empty_json_request
from piazza_api import Piazza
from app.utils import read_credentials


def get_enrolled_courses_from_piazza():
    piazza = Piazza()
    email, password = read_credentials()
    piazza.user_login(email, password)
    enrolled_courses = piazza.get_user_classes()
    return enrolled_courses


class Courses(Resource):

    @verify_non_empty_json_request
    def get(self):
        enrolled_courses = get_enrolled_courses_from_piazza()
        return [{'name': d['name'], 'course_id': d['nid'], 'term': d['term'],
                 'course_num': d['num']} for d in enrolled_courses], 200


class CoursesCourseID(Resource):

    @verify_non_empty_json_request
    def get(self, course_id):
        enrolled_courses = get_enrolled_courses_from_piazza()
        for course in enrolled_courses:
            if course['course_id'] == course_id:
                return course, 200
        return {'message': 'Bad input parameter. Course does not exist.'}, 400


class CourseEnrolled(Resource):

    # @jwt_required()
    def get(self, course_id):
        courses = boto3.resource("dynamodb").Table("Courses")
        exists = courses.get_item(
            Key={
                "course_id": course_id
            }
        ).get("Item")

        if exists is not None:
            enrolled_courses = get_enrolled_courses_from_piazza()
            for course in enrolled_courses:
                if course['course_id'] == course_id:
                    return course, 200
        else:
            return {'message': 'Bad input parameter. Course does not exist.'}, 400

    # @jwt_required()
    def post(self, cid):
        """
        instructor registers the class
        :return:
        """
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
