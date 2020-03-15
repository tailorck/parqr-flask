import uuid
import json
import boto3
import numpy as np
from app.constants import (
    FEEDBACK_MAX_RATING,
    FEEDBACK_MIN_RATING
)


class Feedback(object):

    def __init__(self, max_rating, min_rating, feedback_probability=0.1):
        """ Initialization
            Parameters
            ----------
            max_rating : int
                The maximum rating to accept for a post
            min_rating : int
                The minimum rating to accept for a post
        """

        self.max_rating = max_rating
        self.min_rating = min_rating
        self.feedback_probability = feedback_probability

    def requires_feedback(self):
        """ Given a set of recommendations, decides whether
            to request feedback from the user or not.

            Returns
            -------
            similar_posts : dict
                The same dictionary, but with a boolean flag added for each
                post. The flag is true if feedback should be requested.
        """
        return np.random.random_sample() < self.feedback_probability

    def update_recommendations(self, query_rec_id, similar_posts):
        for key in similar_posts:
            similar_posts[key]['feedback'] = True
        similar_posts['query_rec_id'] = query_rec_id
        return similar_posts

    def save_query_rec_pair(self, cid, query, similar_posts):
        recommended_pids = [similar_posts[score]["pid"] for score in similar_posts.keys()]

        dynamodb = boto3.client('dynamodb')
        query_rec_id = uuid.uuid4()
        query_recommendation_pair = {
                'course_id': cid,
                'uuid': query_rec_id,
                'query': query,
                'recommended_pids': recommended_pids
            }

        dynamodb.put_item(
            TableName='Feedbacks',
            Item=query_recommendation_pair
        )

        return query_rec_id

    def validate_feedback(self, course_id, user_id, query_rec_id, feedback_pid, user_rating):
        """ Performs a sanity check on the feedback.
            Returns true if the feedback is in a valid format
            and holds valid data. Returns false otherwise.

            Parameters
            ----------
            feedback : dict
                The feedback to register
            Returns
            -------
            valid : boolean
                A boolean saying whether the feedback is valid or not
        """

        # Check that the user rating are within the accepted limits
        if (user_rating < self.min_rating) or (user_rating > self.max_rating):
            return False, "Rating must be between {} and {}.".format(self.min_rating, self.max_rating)

        # Check that the query-recommendation pair exists
        dynamodb = boto3.client('dynamodb')
        response = dynamodb.get_item(
            TableName='Feedbacks',
            Key={
                'uuid': {
                    'S': query_rec_id
                }
            }
        )
        print(response)
        query_rec_pair = response.get("Item")
        if not query_rec_pair:
            return False, "The query-recommendation id {} does not exist.".format(query_rec_id)

        # Check that the query string isn't empty
        query = query_rec_pair.get("query").get('S')

        if not query:
            return False, "Invalid query string."

        # Check for valid course id
        # if not Course.objects(course_id=course_id):
        #     return False, "Course {} is currently not supported.".format(course_id)

        # Check that the feedback is for a post that was actually recommended
        recommended_pids = json.loads(query_rec_pair.get("recommended_pids").get('S'))

        if feedback_pid not in recommended_pids:
            return False, "The post id {} is not in the list of suggested posts ids {}.".format(feedback_pid,
                                                                                                recommended_pids)

        # Check that all suggested pids actually exist
        # for pid in recommended_pids:
        #     if not Post.objects(course_id=course_id, post_id=pid):
        #         return False, "Post id {} does not exist for course {}".format(pid, course_id)

        return True, query_rec_pair

    @staticmethod
    def register_feedback(course_id, user_id, query_rec_id, feedback_pid, user_rating):
        """ Registers given feedback in the database.
            Parameters
            ----------
            feedback : dict
                A dictionary with the feedback data.
            Returns
            -------
            success : boolean
                True if the data was registered successfully, false otherwise.
        """

        dynamodb = boto3.client('dynamodb')
        query_rec_pair = dynamodb.get_item(
            TableName='Feedbacks',
            Key={
                'uuid': {
                    'S': query_rec_id
                }
            }
        ).get("Item")

        # If it doesn't exist, return failure
        if not query_rec_pair:
            return False

        # Record the feedback
        dynamodb.update_item(
            TableName='Feedbacks',
            Key={
                'uuid': {
                    'S': query_rec_id
                }
            },
            UpdateExpression="set user_rating = :user_rating_val",
            ExpressionAttributeValues={
                ":user_rating_val": {
                    'N': str(user_rating)
                }
            }
        )

        return True

    @staticmethod
    def unpack_feedback(feedback):
        course_id = feedback["course_id"]
        user_id = feedback["user_id"]
        query_rec_id = feedback["query_rec_id"]
        feedback_pid = feedback["feedback_pid"]
        user_rating = feedback["user_rating"]

        return course_id, user_id, query_rec_id, feedback_pid, user_rating


def lambda_handler(event, context):
    feedback = Feedback(FEEDBACK_MAX_RATING, FEEDBACK_MIN_RATING)
    if event.get("source") == "query":
        similar_posts = event.get("similar_posts")
        course_id = event.get("course_id")
        query = event.get("query")

        query_rec_id = feedback.save_query_rec_pair(course_id, query, similar_posts)
        similar_posts = feedback.update_recommendations(query_rec_id, similar_posts)

        return {"similar_posts": similar_posts}
    else:
        course_id, user_id, query_rec_id, feedback_pid, user_rating = feedback.unpack_feedback(event)
        valid, message = feedback.validate_feedback(course_id, user_id, query_rec_id, feedback_pid, user_rating)

        # If not failed, return invalid usage
        if not valid:
            return {'message': "Feedback contains invalid data." + message}, 400
        success = Feedback.register_feedback(course_id, user_id, query_rec_id, feedback_pid, user_rating)

        if success:
            return {'message': 'success'}, 200

        else:
            return {'message': 'failure'}, 500
