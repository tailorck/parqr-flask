import json
import time

from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from flask import jsonify, request
import boto3

from app.utils import read_credentials
from piazza_api import Piazza


# TODO: Send a request to Parser
def get_enrolled_courses_from_piazza():
    piazza = Piazza()
    email, password = read_credentials()
    piazza.user_login(email, password)
    enrolled_courses = piazza.get_user_classes()
    return enrolled_courses


def mark_active_courses(course_list):
    events = boto3.client('events')

    for course in course_list:
        response = events.describe_rule(
            Name=course.get('course_id')
        )
        if response.get('State') == 'ENABLED':
            course['active'] = True
        else:
            course['active'] = False

    return course_list


class CoursesList(Resource):

    def __init__(self):
        self.enrolled_courses = parser.get_enrolled_courses()
        self.enrolled_courses = mark_active_courses(self.enrolled_courses)

    @jwt_required()
    def get(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('active', type=bool)
        args = arg_parser.parse_args()

        if args.active:
            return jsonify(list(filter(lambda x: x['active'], self.enrolled_courses)))
        else:
            return jsonify(self.enrolled_courses)


class ActiveCourse(Resource):

    def __init__(self):
        self.enrolled_courses = parser.get_enrolled_courses()
        self.enrolled_courses = mark_active_courses(self.enrolled_courses)

    @jwt_required()
    def get(self, course_id):
        active_course = None
        for course in self.enrolled_courses:
            if course.get('course_id') == course_id and course.get('active'):
                active_course = course

        if not active_course:
            return {'message': 'Course does not exist or is not active.'}, 400

        return active_course, 200

    @jwt_required()
    def post(self, course_id):
        """
        instructor registers the class
        :return:
        """
        print('Registering new course: {}'.format(course_id))
        valid_course_id = False
        for course in self.enrolled_courses:
            if course.get('course_id') == course_id:
                valid_course_id = True

        if not valid_course_id:
            return {'message': 'PARQR is not enrolled in course with id {}'.format(course_id)}, 409

        # Create a new event as a cloud cron job
        cloudwatch_events = boto3.client("events")
        rule_arn = cloudwatch_events.put_rule(
            Name=course_id,
            ScheduleExpression='rate(15 minutes)',
            State='ENABLED'
        ).get('RuleArn')

        if not rule_arn:
            print("{}: Error creating cloudwatch event".format(course_id))
            return {'message': 'Internal Server Error'}, 500

        # Create a lambda permission object so cloudwatch events can call the lambda
        lambda_client = boto3.client('lambda')
        # TODO: Inject new environment variable based upon master or dev
        lambda_response = lambda_client.add_permission(
            FunctionName='Parser:PROD',
            StatementId="{}-{}".format(course_id, str(int(time.time()))),
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )
        if not lambda_response.get('Statement'):
            print("Error creating lambda permission course")
            print(lambda_response)
            return {'message': 'Internal Server Error'}, 500

        # Set the lambda as the cloudwatch event target
        lambda_arn = json.loads(lambda_response.get('Statement')).get('Resource')
        target_response = cloudwatch_events.put_targets(
            Rule=course_id,
            Targets=[
                {
                    'Id': "{}-{}".format(course_id, str(int(time.time()))),
                    'Arn': lambda_arn
                }
            ]
        )

        if target_response.get('FailedEntryCount') > 0:
            print("Error putting cloudwatch event target")
            return {'message': 'Internal Server Error'}, 500

    @jwt_required()
    def delete(self, course_id):
        print('Deregistering course: {}'.format(course_id))

        cloudwatch_events = boto3.client("events")
        cloudwatch_events.disable_rule(
            Name=course_id
        )

        return {'course_id disabled': course_id}, 200


class FindCourseByCourseID(Resource):

    def get(self, course_id):
        enrolled_courses = get_enrolled_courses_from_piazza()
        for course in enrolled_courses:
            if course['course_id'] == course_id:
                return course, 200

        return {'message': 'Bad input parameter. Course does not exist.'}, 400
