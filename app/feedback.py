from app.models import Course, Post, StudentFeedbackRecord, QueryRecommendationPair
from app.constants import DATETIME_FORMAT
from datetime import datetime
from bson.objectid import ObjectId

import numpy as np


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

    def request_feedback(self, similar_posts):
        """ Given a set of recommendations, decides whether
            to request feedback from the user or not.

            TODO: Change function to use a strategy
            rather than pure randomness.
            Parameters
            ----------
            similar_posts : dict
                A dictionary with the posts suggested by PARQR.
            Returns
            -------
            similar_posts : dict
                The same dictionary, but with a boolean flag added for each
                post. The flag is true if feedback should be requested.
        """

        if np.random.random_sample() < self.feedback_probability:
            for key in similar_posts.keys():
                if key != "id":
                    similar_posts[key]['feedback'] = True

        return similar_posts

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

        # Check that the query-recommendation id is valid
        if not ObjectId.is_valid(query_rec_id):
            return False, "The query-recommendation id {} is not valid.".format(query_rec_id)

        # Check that the query-recommendation pair exists
        query_rec_pair = QueryRecommendationPair.objects.with_id(query_rec_id)

        if not query_rec_pair:
            return False, "The query-recommendation id {} does not exist.".format(query_rec_id)

        # Check that the query string isn't empty
        query = query_rec_pair.query

        if not query:
            return False, "Invalid query string."

        # Check for valid course id
        if not Course.objects(course_id=course_id):
            return False, "Course {} is currently not supported.".format(course_id)

        # Check that the feedback is for a post that was actually recommended
        recommended_pids = query_rec_pair.recommended_pids

        if feedback_pid not in recommended_pids:
            return False, "The post id {} is not in the list of suggested posts ids {}.".format(feedback_pid,
                                                                                                recommended_pids)

        # Check that all suggested pids actually exist
        for pid in recommended_pids:
            if not Post.objects(course_id=course_id, post_id=pid):
                return False, "Post id {} does not exist for course {}".format(pid, course_id)

        return True, ""

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

        time = datetime.now()

        # Get the course
        course = Course.objects(course_id=course_id)

        # If it doesn't exist, return failure
        if not course:
            return False

        # Get the query-recommendation pair
        query_rec_pair = QueryRecommendationPair.objects.with_id(query_rec_id)

        # If it doesn't exist, return failure
        if not query_rec_pair:
            return False

        # Record the feedback
        feedback_record = StudentFeedbackRecord(course_id=course_id,
                                                user_id=user_id,
                                                time=time,
                                                query_rec_pair=query_rec_pair,
                                                feedback_pid=feedback_pid,
                                                user_rating=user_rating).save()

        return True

    @staticmethod
    def unpack_feedback(feedback):
        course_id = feedback["course_id"]
        user_id = feedback["user_id"]
        query_rec_id = feedback["query_recommendation_id"]
        feedback_pid = feedback["feedback_pid"]
        user_rating = feedback["user_rating"]

        return course_id, user_id, query_rec_id, feedback_pid, user_rating