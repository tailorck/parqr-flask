import unittest
import os
from app import api
import mock
import boto3
import json
from decimal import Decimal


class TestHelloWorldAPI(unittest.TestCase):
    HELLO_WORLD_EVENT = {
        'body': '{\r\n'
                '  "event_type": "event",\r\n'
                '  "user_id": 867481538782578,\r\n'
                '  "course_id": "jze974ouf142qb",\r\n'
                '  "event_data": "data"\r\n'
                '}',
        'headers': {'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Content-Type': 'application/json',
                    'Host': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                    'Postman-Token': 'd72e00cd-7120-484e-99da-3694563d05ed',
                    'User-Agent': 'PostmanRuntime/7.22.0',
                    'X-Amzn-Trace-Id': 'Root=1-5e530337-ab17dec010055300514885c0',
                    'X-Forwarded-For': '128.61.2.250',
                    'X-Forwarded-Port': '443',
                    'X-Forwarded-Proto': 'https'},
        'httpMethod': 'GET',
        'isBase64Encoded': False,
        'multiValueHeaders': {'Accept': ['*/*'],
                              'Accept-Encoding': ['gzip, deflate, br'],
                              'Cache-Control': ['no-cache'],
                              'Content-Type': ['application/json'],
                              'Host': ['7uzke7qgw3.execute-api.us-east-2.amazonaws.com'],
                              'Postman-Token': ['d72e00cd-7120-484e-99da-3694563d05ed'],
                              'User-Agent': ['PostmanRuntime/7.22.0'],
                              'X-Amzn-Trace-Id': ['Root=1-5e530337-ab17dec010055300514885c0'],
                              'X-Forwarded-For': ['128.61.2.250'],
                              'X-Forwarded-Port': ['443'],
                              'X-Forwarded-Proto': ['https']},
        'multiValueQueryStringParameters': None,
        'path': '/',
        'pathParameters': None,
        'queryStringParameters': None,
        'requestContext': {'accountId': '095551794161',
                           'apiId': '7uzke7qgw3',
                           'domainName': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                           'domainPrefix': '7uzke7qgw3',
                           'extendedRequestId': 'IX1wrHVuiYcF0Wg=',
                           'httpMethod': 'GET',
                           'identity': {'accessKey': None,
                                        'accountId': None,
                                        'caller': None,
                                        'cognitoAuthenticationProvider': None,
                                        'cognitoAuthenticationType': None,
                                        'cognitoIdentityId': None,
                                        'cognitoIdentityPoolId': None,
                                        'principalOrgId': None,
                                        'sourceIp': '128.61.2.250',
                                        'user': None,
                                        'userAgent': 'PostmanRuntime/7.22.0',
                                        'userArn': None},
                           'path': '/v2/',
                           'protocol': 'HTTP/1.1',
                           'requestId': '73c554f8-de97-4661-8dfa-21976a281c0b',
                           'requestTime': '23/Feb/2020:22:56:55 +0000',
                           'requestTimeEpoch': 1582498615468,
                           'resourceId': '9082ewim44',
                           'resourcePath': '/',
                           'stage': 'v2'},
        'resource': '/',
        'stageVariables': None}
    CONTEXT = {}

    HELLO_WORLD_RESPONSE = {'statusCode': '200',
                            'headers': {'Content-Type': 'text/html; charset=utf-8',
                                        'Content-Length': '13'},
                            'isBase64Encoded': False,
                            'body': 'Hello, World!'}

    def test_hello_world(self):
        response = api.lambda_handler(TestHelloWorldAPI.HELLO_WORLD_EVENT, TestHelloWorldAPI.CONTEXT)

        assert TestHelloWorldAPI.HELLO_WORLD_RESPONSE == response


def mock_mark_active_courses(courses):
    return json.loads('[{"active": true, "course_id": "j8rf9vx65vl23t", "course_num": "CS '
                      '007", "name": "Parqr Test Course", "term": "Fall 2017"}]')


def mock_get_enrolled_courses_from_piazza():
    return json.loads(
        '[{"course_id": "j8rf9vx65vl23t", "course_num": "CS '                                           '007", '
        '"name": "Parqr Test Course", "term": "Fall 2017"}] ')


class TestCoursesAPI(unittest.TestCase):
    COURSES_EVENT = {'body': '{}',
                     'headers': {'Accept': '*/*',
                                 'Accept-Encoding': 'gzip, deflate, br',
                                 'Cache-Control': 'no-cache',
                                 'Content-Type': 'application/json',
                                 'Host': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                                 'Postman-Token': '8b57a10f-7171-4f41-a5e5-dbdf1bf19bd5',
                                 'User-Agent': 'PostmanRuntime/7.22.0',
                                 'X-Amzn-Trace-Id': 'Root=1-5e53204a-d4157a694ddf9c5daec88e26',
                                 'X-Forwarded-For': '128.61.2.250',
                                 'X-Forwarded-Port': '443',
                                 'X-Forwarded-Proto': 'https'},
                     'httpMethod': 'GET',
                     'isBase64Encoded': False,
                     'multiValueHeaders': {'Accept': ['*/*'],
                                           'Accept-Encoding': ['gzip, deflate, br'],
                                           'Cache-Control': ['no-cache'],
                                           'Content-Type': ['application/json'],
                                           'Host': ['7uzke7qgw3.execute-api.us-east-2.amazonaws.com'],
                                           'Postman-Token': ['8b57a10f-7171-4f41-a5e5-dbdf1bf19bd5'],
                                           'User-Agent': ['PostmanRuntime/7.22.0'],
                                           'X-Amzn-Trace-Id': ['Root=1-5e53204a-d4157a694ddf9c5daec88e26'],
                                           'X-Forwarded-For': ['128.61.2.250'],
                                           'X-Forwarded-Port': ['443'],
                                           'X-Forwarded-Proto': ['https']},
                     'multiValueQueryStringParameters': None,
                     'path': '/courses',
                     'pathParameters': {'proxy': 'courses'},
                     'queryStringParameters': None,
                     'requestContext': {'accountId': '095551794161',
                                        'apiId': '7uzke7qgw3',
                                        'domainName': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                                        'domainPrefix': '7uzke7qgw3',
                                        'extendedRequestId': 'IYH7sFFUCYcFS_A=',
                                        'httpMethod': 'GET',
                                        'identity': {'accessKey': None,
                                                     'accountId': None,
                                                     'caller': None,
                                                     'cognitoAuthenticationProvider': None,
                                                     'cognitoAuthenticationType': None,
                                                     'cognitoIdentityId': None,
                                                     'cognitoIdentityPoolId': None,
                                                     'principalOrgId': None,
                                                     'sourceIp': '128.61.2.250',
                                                     'user': None,
                                                     'userAgent': 'PostmanRuntime/7.22.0',
                                                     'userArn': None},
                                        'path': '/v2/courses',
                                        'protocol': 'HTTP/1.1',
                                        'requestId': 'd8b68246-e9cb-4a44-8d71-bb3a103012c4',
                                        'requestTime': '24/Feb/2020:01:00:58 +0000',
                                        'requestTimeEpoch': 1582506058778,
                                        'resourceId': 'ycv30v',
                                        'resourcePath': '/{proxy+}',
                                        'stage': 'v2'},
                     'resource': '/{proxy+}',
                     'stageVariables': None}
    CONTEXT = {}

    COURSES_RESPONSE = {
        'body': '[\n'
                '  {\n'
                '    "active": true, \n'
                '    "course_id": "j8rf9vx65vl23t", \n'
                '    "course_num": "CS 007", \n'
                '    "name": "Parqr Test Course", \n'
                '    "term": "Fall 2017"\n'
                '  }\n'
                ']\n',
        'headers': {'Content-Length': '156', 'Content-Type': 'application/json'},
        'isBase64Encoded': False,
        'statusCode': '200'}

    @mock.patch('app.resources.course.mark_active_courses', side_effect=mock_mark_active_courses)
    @mock.patch('app.resources.course.get_enrolled_courses_from_piazza',
                side_effect=mock_get_enrolled_courses_from_piazza)
    def test_get(self, mock_mark_active_courses_function, mock_boto_function):
        response = api.lambda_handler(TestCoursesAPI.COURSES_EVENT, TestCoursesAPI.CONTEXT)
        assert TestCoursesAPI.COURSES_RESPONSE == response


class TestCourseAPI(unittest.TestCase):
    COURSE_GET_EVENT = {
        'body': '{}',
        'headers': {'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Content-Type': 'application/json',
                    'Host': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                    'Postman-Token': 'ca2a6232-b381-4811-957e-298c53d01674',
                    'User-Agent': 'PostmanRuntime/7.22.0',
                    'X-Amzn-Trace-Id': 'Root=1-5e5419d9-f2749846d105935160391b59',
                    'X-Forwarded-For': '128.61.5.213',
                    'X-Forwarded-Port': '443',
                    'X-Forwarded-Proto': 'https'},
        'httpMethod': 'GET',
        'isBase64Encoded': False,
        'multiValueHeaders': {'Accept': ['*/*'],
                              'Accept-Encoding': ['gzip, deflate, br'],
                              'Cache-Control': ['no-cache'],
                              'Content-Type': ['application/json'],
                              'Host': ['7uzke7qgw3.execute-api.us-east-2.amazonaws.com'],
                              'Postman-Token': ['ca2a6232-b381-4811-957e-298c53d01674'],
                              'User-Agent': ['PostmanRuntime/7.22.0'],
                              'X-Amzn-Trace-Id': ['Root=1-5e5419d9-f2749846d105935160391b59'],
                              'X-Forwarded-For': ['128.61.5.213'],
                              'X-Forwarded-Port': ['443'],
                              'X-Forwarded-Proto': ['https']},
        'multiValueQueryStringParameters': None,
        'path': '/course/j8rf9vx65vl23t',
        'pathParameters': {'proxy': 'course/j8rf9vx65vl23t'},
        'queryStringParameters': None,
        'requestContext': {'accountId': '095551794161',
                           'apiId': '7uzke7qgw3',
                           'domainName': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                           'domainPrefix': '7uzke7qgw3',
                           'extendedRequestId': 'Iaj59F6ZCYcFSxA=',
                           'httpMethod': 'GET',
                           'identity': {'accessKey': None,
                                        'accountId': None,
                                        'caller': None,
                                        'cognitoAuthenticationProvider': None,
                                        'cognitoAuthenticationType': None,
                                        'cognitoIdentityId': None,
                                        'cognitoIdentityPoolId': None,
                                        'principalOrgId': None,
                                        'sourceIp': '128.61.5.213',
                                        'user': None,
                                        'userAgent': 'PostmanRuntime/7.22.0',
                                        'userArn': None},
                           'path': '/v2/course/j8rf9vx65vl23t',
                           'protocol': 'HTTP/1.1',
                           'requestId': 'd00afb81-a3dd-41e5-b880-d9b9af08bed3',
                           'requestTime': '24/Feb/2020:18:45:45 +0000',
                           'requestTimeEpoch': 1582569945217,
                           'resourceId': 'ycv30v',
                           'resourcePath': '/{proxy+}',
                           'stage': 'v2'},
        'resource': '/{proxy+}',
        'stageVariables': None}
    CONTEXT = {}

    COURSE_GET_RESPONSE = {
        'statusCode': '200',
        'headers': {
            'Content-Type': 'application/json',
            'Content-Length': '106'},
        'isBase64Encoded': False,
        'body': '{"course_id": "j8rf9vx65vl23t", "course_num": "CS 007", "name": "Parqr Test '
                'Course", "term": "Fall 2017"}\n'}

    @mock.patch('app.resources.course.get_enrolled_courses_from_piazza', side_effect=mock_get_enrolled_courses_from_piazza)
    def test_get(self, mock_get_enrolled_courses_from_piazza_function):
        response = api.lambda_handler(TestCourseAPI.COURSE_GET_EVENT, TestCourseAPI.CONTEXT)
        assert TestCourseAPI.COURSE_GET_RESPONSE == response


class TestActiveCourseAPI(unittest.TestCase):
    COURSE_GET_EVENT = {
        'body': '{}',
        'headers': {'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Content-Type': 'application/json',
                    'Host': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                    'Postman-Token': '2d82ea78-81e9-4342-b6e2-49b9d2ed26da',
                    'User-Agent': 'PostmanRuntime/7.22.0',
                    'X-Amzn-Trace-Id': 'Root=1-5e5443b8-eb16a35c33dc0bbc9cec9798',
                    'X-Forwarded-For': '128.61.5.213',
                    'X-Forwarded-Port': '443',
                    'X-Forwarded-Proto': 'https'},
        'httpMethod': 'GET',
        'isBase64Encoded': False,
        'multiValueHeaders': {'Accept': ['*/*'],
                              'Accept-Encoding': ['gzip, deflate, br'],
                              'Cache-Control': ['no-cache'],
                              'Content-Type': ['application/json'],
                              'Host': ['7uzke7qgw3.execute-api.us-east-2.amazonaws.com'],
                              'Postman-Token': ['2d82ea78-81e9-4342-b6e2-49b9d2ed26da'],
                              'User-Agent': ['PostmanRuntime/7.22.0'],
                              'X-Amzn-Trace-Id': ['Root=1-5e5443b8-eb16a35c33dc0bbc9cec9798'],
                              'X-Forwarded-For': ['128.61.5.213'],
                              'X-Forwarded-Port': ['443'],
                              'X-Forwarded-Proto': ['https']},
        'multiValueQueryStringParameters': None,
        'path': '/courses',
        'pathParameters': {'proxy': 'courses'},
        'queryStringParameters': None,
        'requestContext': {'accountId': '095551794161',
                           'apiId': '7uzke7qgw3',
                           'domainName': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                           'domainPrefix': '7uzke7qgw3',
                           'extendedRequestId': 'Ia-E3FmyCYcFnTw=',
                           'httpMethod': 'GET',
                           'identity': {'accessKey': None,
                                        'accountId': None,
                                        'caller': None,
                                        'cognitoAuthenticationProvider': None,
                                        'cognitoAuthenticationType': None,
                                        'cognitoIdentityId': None,
                                        'cognitoIdentityPoolId': None,
                                        'principalOrgId': None,
                                        'sourceIp': '128.61.5.213',
                                        'user': None,
                                        'userAgent': 'PostmanRuntime/7.22.0',
                                        'userArn': None},
                           'path': '/v2/courses',
                           'protocol': 'HTTP/1.1',
                           'requestId': '439a2191-6f04-4394-8917-46857942ace3',
                           'requestTime': '24/Feb/2020:21:44:24 +0000',
                           'requestTimeEpoch': 1582580664657,
                           'resourceId': 'ycv30v',
                           'resourcePath': '/{proxy+}',
                           'stage': 'v2'},
        'resource': '/{proxy+}',
        'stageVariables': None}
    CONTEXT = {}

    COURSE_GET_RESPONSE = {
        'body': '[\n'
                '  {\n'
                '    "active": true, \n'
                '    "course_id": "j8rf9vx65vl23t", \n'
                '    "course_num": "CS 007", \n'
                '    "name": "Parqr Test Course", \n'
                '    "term": "Fall 2017"\n'
                '  }\n'
                ']\n',
        'headers': {'Content-Length': '156', 'Content-Type': 'application/json'},
        'isBase64Encoded': False,
        'statusCode': '200'}

    @mock.patch('app.resources.course.mark_active_courses', side_effect=mock_mark_active_courses)
    @mock.patch('app.resources.course.get_enrolled_courses_from_piazza', side_effect=mock_get_enrolled_courses_from_piazza)
    def test_get(self, mock_mark_active_courses_function, mock_get_enrolled_courses_from_piazza_active_function):
        response = api.lambda_handler(TestActiveCourseAPI.COURSE_GET_EVENT, TestActiveCourseAPI.CONTEXT)
        assert TestActiveCourseAPI.COURSE_GET_RESPONSE == response


def mock_get_recs_from_parqr():
    mock_boto3 = mock.Mock()
    mock_response_body = mock.Mock()
    mock_encoded_body = mock.Mock()
    mock_encoded_body.decode.return_value = '{"0.1617989443268492": {"pid": 8, "subject": "alpha beta performing ' \
                                            'better than Iterative Deepening", "s_answer": false, "i_answer": true, ' \
                                            '"feedback": false}} '
    mock_response_body.read.return_value = mock_encoded_body
    mock_boto3.invoke.return_value = {
        'Payload': mock_response_body
    }
    return mock_boto3


class TestQueryStudentAPI(unittest.TestCase):
    QUERY_EVENT = {
        'body': '{\n\t"query": "How do I do alpha beta pruning"\n}',
        'headers': {'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Content-Type': 'application/json',
                    'Host': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                    'Postman-Token': 'a2f64f50-20a3-4e06-8871-a966f4244427',
                    'User-Agent': 'PostmanRuntime/7.22.0',
                    'X-Amzn-Trace-Id': 'Root=1-5e544d85-b6ac27d81f2b19d01a0c3cbc',
                    'X-Forwarded-For': '128.61.5.213',
                    'X-Forwarded-Port': '443',
                    'X-Forwarded-Proto': 'https'},
        'httpMethod': 'POST',
        'isBase64Encoded': False,
        'multiValueHeaders': {'Accept': ['*/*'],
                              'Accept-Encoding': ['gzip, deflate, br'],
                              'Cache-Control': ['no-cache'],
                              'Content-Type': ['application/json'],
                              'Host': ['7uzke7qgw3.execute-api.us-east-2.amazonaws.com'],
                              'Postman-Token': ['a2f64f50-20a3-4e06-8871-a966f4244427'],
                              'User-Agent': ['PostmanRuntime/7.22.0'],
                              'X-Amzn-Trace-Id': ['Root=1-5e544d85-b6ac27d81f2b19d01a0c3cbc'],
                              'X-Forwarded-For': ['128.61.5.213'],
                              'X-Forwarded-Port': ['443'],
                              'X-Forwarded-Proto': ['https']},
        'multiValueQueryStringParameters': None,
        'path': '/course/j8rf9vx65vl23t/query/student',
        'pathParameters': {'proxy': 'course/j8rf9vx65vl23t/query/student'},
        'queryStringParameters': None,
        'requestContext': {'accountId': '095551794161',
                           'apiId': '7uzke7qgw3',
                           'domainName': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                           'domainPrefix': '7uzke7qgw3',
                           'extendedRequestId': 'IbEM3G9iCYcF66w=',
                           'httpMethod': 'POST',
                           'identity': {'accessKey': None,
                                        'accountId': None,
                                        'caller': None,
                                        'cognitoAuthenticationProvider': None,
                                        'cognitoAuthenticationType': None,
                                        'cognitoIdentityId': None,
                                        'cognitoIdentityPoolId': None,
                                        'principalOrgId': None,
                                        'sourceIp': '128.61.5.213',
                                        'user': None,
                                        'userAgent': 'PostmanRuntime/7.22.0',
                                        'userArn': None},
                           'path': '/v2/course/j8rf9vx65vl23t/query/student',
                           'protocol': 'HTTP/1.1',
                           'requestId': '151b3984-175d-4557-ae86-f8d315f88cd5',
                           'requestTime': '24/Feb/2020:22:26:13 +0000',
                           'requestTimeEpoch': 1582583173457,
                           'resourceId': 'ycv30v',
                           'resourcePath': '/{proxy+}',
                           'stage': 'v2'},
        'resource': '/{proxy+}',
        'stageVariables': None}
    CONTEXT = {}

    QUERY_RESPONSE = {'statusCode': '200',
                      'headers': {
                          'Content-Type': 'application/json',
                          'Content-Length': '159'},
                      'isBase64Encoded': False,
                      'body': '{"0.1617989443268492": {"pid": 8, "subject": "alpha beta performing better than '
                              'Iterative Deepening", "s_answer": false, "i_answer": true, "feedback": false}}\n'}

    @mock.patch('app.resources.query.get_boto3_lambda', side_effect=mock_get_recs_from_parqr)
    def test_post(self, mock_get_recs_from_parqr_function):
        response = api.lambda_handler(TestQueryStudentAPI.QUERY_EVENT, TestQueryStudentAPI.CONTEXT)
        assert TestQueryStudentAPI.QUERY_RESPONSE == response


def mock_get_posts_table():
    mock_boto3 = mock.Mock()
    mock_boto3.scan.return_value = {
        "Items": [
            {
                'subject': 'oh henlo',
                'post_type': 'question',
                'num_unresolved_followups': Decimal('0'),
                'followups': [],
                'course_id': 'j8rf9vx65vl23t',
                'post_id': Decimal('18'),
                'created': Decimal('1581482976'),
                'num_views': Decimal('2'),
                'tags': ['hw4', 'student', 'unanswered'],
                'body': 'wassup'
            }
        ]
    }
    return mock_boto3


def mock_is_course_id_valid(course_id):
    return True


class TestStudentRecommendationAPI(unittest.TestCase):
    QUERY_EVENT = {
        'body': None,
        'headers': {'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Content-Type': 'application/json',
                    'Host': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                    'Postman-Token': '42f2a39a-0071-4566-b98f-ebd2299b4d29',
                    'User-Agent': 'PostmanRuntime/7.22.0',
                    'X-Amzn-Trace-Id': 'Root=1-5e54550a-d2648054cee70ff3d96ea89c',
                    'X-Forwarded-For': '128.61.5.213',
                    'X-Forwarded-Port': '443',
                    'X-Forwarded-Proto': 'https'},
        'httpMethod': 'GET',
        'isBase64Encoded': False,
        'multiValueHeaders': {'Accept': ['*/*'],
                              'Accept-Encoding': ['gzip, deflate, br'],
                              'Cache-Control': ['no-cache'],
                              'Content-Type': ['application/json'],
                              'Host': ['7uzke7qgw3.execute-api.us-east-2.amazonaws.com'],
                              'Postman-Token': ['42f2a39a-0071-4566-b98f-ebd2299b4d29'],
                              'User-Agent': ['PostmanRuntime/7.22.0'],
                              'X-Amzn-Trace-Id': ['Root=1-5e54550a-d2648054cee70ff3d96ea89c'],
                              'X-Forwarded-For': ['128.61.5.213'],
                              'X-Forwarded-Port': ['443'],
                              'X-Forwarded-Proto': ['https']},
        'multiValueQueryStringParameters': None,
        'path': '/courses/j8rf9vx65vl23t/recommendation/student',
        'pathParameters': {'proxy': 'courses/j8rf9vx65vl23t/recommendation/student'},
        'queryStringParameters': None,
        'requestContext': {'accountId': '095551794161',
                           'apiId': '7uzke7qgw3',
                           'domainName': '7uzke7qgw3.execute-api.us-east-2.amazonaws.com',
                           'domainPrefix': '7uzke7qgw3',
                           'extendedRequestId': 'IbI5mEYTiYcFlgQ=',
                           'httpMethod': 'GET',
                           'identity': {'accessKey': None,
                                        'accountId': None,
                                        'caller': None,
                                        'cognitoAuthenticationProvider': None,
                                        'cognitoAuthenticationType': None,
                                        'cognitoIdentityId': None,
                                        'cognitoIdentityPoolId': None,
                                        'principalOrgId': None,
                                        'sourceIp': '128.61.5.213',
                                        'user': None,
                                        'userAgent': 'PostmanRuntime/7.22.0',
                                        'userArn': None},
                           'path': '/v2/courses/j8rf9vx65vl23t/recommendation/student',
                           'protocol': 'HTTP/1.1',
                           'requestId': 'd13b7fa7-ee9f-46af-8e18-130db6c8bad9',
                           'requestTime': '24/Feb/2020:22:58:18 +0000',
                           'requestTimeEpoch': 1582585098193,
                           'resourceId': 'ycv30v',
                           'resourcePath': '/{proxy+}',
                           'stage': 'v2'},
        'resource': '/{proxy+}',
        'stageVariables': None}
    CONTEXT = {}

    QUERY_RESPONSE = {
        'statusCode': '200', 'headers': {'Content-Type': 'application/json', 'Content-Length': '159'},
        'isBase64Encoded': False,
        'body': '{"message": "success", "recommendations": [{"title": "oh henlo", "post_id": 18, '
                '"properties": ["0 followups", "2 views", "Tags - hw4, student, unanswered"]}]}\n'}

    @mock.patch('app.statistics.get_posts_table', side_effect=mock_get_posts_table)
    @mock.patch('app.statistics.is_course_id_valid', side_effect=mock_is_course_id_valid)
    def test_get(self, mock_get_posts_table_function, mock_is_course_id_valid_function):
        response = api.lambda_handler(TestStudentRecommendationAPI.QUERY_EVENT, TestStudentRecommendationAPI.CONTEXT)
        assert TestStudentRecommendationAPI.QUERY_RESPONSE == response


if __name__ == "__main__":
    unittest.main()
