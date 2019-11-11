from datetime import datetime
import time

import boto3
from bs4 import BeautifulSoup
from piazza_api import Piazza
from piazza_api.exceptions import AuthenticationError, RequestError

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
dynamodb = boto3.client('dynamodb')
dynamodb_resource = boto3.resource('dynamodb')


def read_credentials():
    """Method to read encrypted .login file for Piazza username and password"""
    return 'parqrdevteam@gmail.com', 'parqrproducers'


class Parser(object):

    def __init__(self):
        """Initialize the Piazza object and login with the encrypted username
        and password
        """
        self._piazza = Piazza()
        self._login()

    def _login(self):
        """Try to read the login file else prompt the user for manual login"""
        try:
            email, password = read_credentials()
            self._piazza.user_login(email, password)
        except IOError:
            print("File not found. Use encrypt_login.py to "
                  "create encrypted password store")
        except (UnicodeDecodeError, AuthenticationError) as e:
            print("Incorrect Email/Password found in "
                  "encrypted file store")

    def get_enrolled_courses(self):
        enrolled_courses = self._piazza.get_user_classes()
        return [{'name': d['name'], 'course_id': d['nid'], 'term': d['term'],
                 'course_num': d['num']} for d in enrolled_courses]

    def update_posts(self, course_id):
        """Creates a thread task to update all posts in a course

        Retrieves all new posts in course that are not already in database
        and updates old posts that have been modified

        Parameters
        ----------
        course_id : str
            The course id of the class to be updated


        Returns
        -------
        success : boolean
            True if course parsed without any errors. False, otherwise.
        """
        print("Parsing posts for course: {}".format(course_id))
        network = self._piazza.network(course_id)
        stats = network.get_statistics()

        try:
            total_questions = stats['total']['questions']
        except KeyError:
            print('Unable to get valid statistics for course_id: {}'
                  .format(course_id))
            return False

        # Get handle to the corresponding course document or create a new one
        table_name = "course_" + course_id
        try:
            # TODO: test if table will trigger exception => (dynamodb.Table(table_name))
            _ = dynamodb.describe_table(TableName=table_name)
        except dynamodb.exceptions.ResourceNotFoundException:
            enrolled_courses = self._piazza.get_user_classes()
            for enrolled_course in enrolled_courses:
                if enrolled_course["nid"] == course_id:
                    course_name = enrolled_course["name"]
                    course_number = enrolled_course["num"]
                    course_term = enrolled_course["term"]

                    dynamodb.create_table(
                        TableName=table_name,
                        KeySchema=[
                            {
                                'AttributeName': 'post_id',
                                'KeyType': 'HASH'  # Partition key
                            }
                        ],
                        AttributeDefinitions=[
                            {
                                'AttributeName': 'post_id',
                                'AttributeType': 'N'
                            }
                        ],
                        ProvisionedThroughput={
                            'ReadCapacityUnits': 10,
                            'WriteCapacityUnits': 10
                        },
                        Tags=[
                            {
                                'Key': 'name',
                                'Value': course_name
                            },
                            {
                                'Key': 'num',
                                'Value': course_number
                            },
                            {
                                'Key': 'term',
                                'Value': course_term
                            }
                        ]
                    )
                    dynamodb_resource.Table(table_name).wait_until_exists()
        course = dynamodb_resource.Table(table_name)

        current_pids = set()
        start_time = time.time()
        for pid in range(1, total_questions + 1):
            # Get the post if available
            try:
                post = network.get_post(pid)
            except RequestError:
                continue

            # Skip deleted and private posts
            if post['status'] == 'deleted' or post['status'] == 'private':
                continue

            # If the post is neither deleted nor private, it should be in the db
            current_pids.add(pid)

            # TODO: Parse the type of the post, to indicate if the post is
            # a note/announcement

            # Extract the subject, body, and tags from post
            subject, body, tags, post_type = self._extract_question_details(post)

            # Extract number of unique views of the post
            num_views = post['unique_views']

            # Get creation time
            created = datetime.strptime(post['created'], DATETIME_FORMAT)
            # Extract number of unresolved followups (if any)
            num_unresolved_followups = self._extract_num_unresolved(post)

            # Extract the student and instructor answers if applicable
            s_answer, i_answer = self._extract_answers(post)

            # Extract the followups and feedbacks if applicable
            followups = self._extract_followups(post)

            # insert post and add to course's post list
            item = {
                "post_id": pid,
                "created": int(created.timestamp()),
                "subject": subject,
                "body": body,
                "tags": tags,
                "post_type": post_type,
                "s_answer": s_answer,
                "i_answer": i_answer,
                "followups": followups,
                "num_unresolved_followups": num_unresolved_followups,
                "num_views": num_views
            }
            print(item)
            try:
                course.put_item(
                    Item=item
                )
            except:
                print("ValidationException")
                current_pids.remove(pid)
                continue

        # Get all the posts for this course in the db
        db_pids = set(range(1, total_questions + 1))

        # Delete pids which are in the db but aren't one of the current pids
        pids_to_delete = db_pids - current_pids
        for pid in pids_to_delete:
            course.delete_item(
                Key={
                    "post_id": pid
                }
            )
            print("Deleted post {} while parsing course_id {} ".format(pid, course_id))

        # TODO: Figure out another way to verify whether the current user has
        # access to a class.
        # In the event the course_id was invalid or no posts were parsed,
        # delete course object # TODO: Should we delete the table?
        if len(current_pids) == 0:
            print('Unable to parse posts for course: {}. Please '
                  'confirm that the piazza user has access to this '
                  'course'.format(course_id))
            # Course.objects(course_id=course_id).delete()
            return False

        end_time = time.time()
        time_elapsed = end_time - start_time
        print('Course updated. {} posts scraped in: '
              '{:.2f}s'.format(total_questions, time_elapsed))

        return True

    def _extract_num_unresolved(self, post):
        if len(post['children']) > 0:
            unresolved_list = [post['children'][i]['no_answer']
                               for i in range(len(post['children']))
                               if post['children'][i]['type'] == 'followup']
            return sum(unresolved_list)
        else:
            return 0

    def _extract_question_details(self, post):
        """Retrieves information pertaining to the question in the piazza post

        Parameters
        ----------
        post : dict
            An object including  post information retrieved from a
            piazza_api call

        Returns
        -------
        subject : str
            The subject of the piazza post
        parsed_body : str
            The body of the post without html tags
        tags : list
            A list of the tags or folders that the post belonged to
        """
        subject = post['history'][0]['subject']
        html_body = post['history'][0]['content']
        parsed_body = BeautifulSoup(html_body, 'html.parser').get_text()
        if parsed_body == "":
            parsed_body = None
        tags = post['tags']
        post_type = post['type']
        return subject, parsed_body, tags, post_type

    def _extract_answers(self, post):
        """Retrieves information pertaining to the answers of the piazza post

        Parameters
        ----------
        post : dict
            An object including the post information retrieved from a
            piazza_api call

        Returns
        -------
        s_answer : str
            The student answer to the post if available (Default = None).
        i_answer : str
            The instructor answer to the post if available (Default = None).
        """
        s_answer, i_answer = None, None
        for response in post['children']:
            if response['type'] == 's_answer':
                html_text = response['history'][0]['content']
                s_answer = BeautifulSoup(html_text, 'html.parser').get_text()
            elif response['type'] == 'i_answer':
                html_text = response['history'][0]['content']
                i_answer = BeautifulSoup(html_text, 'html.parser').get_text()

        return s_answer, i_answer

    def _extract_followups(self, post):
        """Retrieves information pertaining to the followups and feedbacks of
        the piazza post

        Parameters
        ----------
        post : dict
            An object including the post information retrieved from a
            piazza_api call

        Returns
        -------
        followups : list
            The followup discussions for a post if available, which might
            contain feedbacks as well (Default = []).
        """
        followups = []
        for child in post['children']:

            data = {}
            if child['type'] == 'followup':
                html_text = child['subject']
                soup = BeautifulSoup(html_text, 'html.parser')
                data['text'] = soup.get_text()

                responses = []
                if child['children']:
                    for activity in child['children']:
                        html_text = activity['subject']
                        soup = BeautifulSoup(html_text, 'html.parser')
                        responses.append(soup.get_text())

                data['responses'] = responses

                followups.append(data)

        return followups


def lambda_handler(event, context):
    print("Event: {}".format(event))
    print("Context: {}".format(context))
    course_id = event['course_id']
    print("Course ID: {}".format(course_id))

    parser = Parser()
    success = parser.update_posts(course_id)
    if success:
        print("Successfully parsed")
    else:
        print("Error parsing")
