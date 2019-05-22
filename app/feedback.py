from app.models import Course, Post, StudentFeedbackRecord
from app.constants import DATETIME_FORMAT
from datetime import datetime


import numpy as np


class Feedback(object):

    def __init__(self, max_rating, min_rating):
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

        if np.random.random_sample() < 0.1:
            for score in similar_posts.keys():
                similar_posts[score]["feedback"] = True

        return similar_posts


    def register_feedback(self, feedback):
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

        # Extract information from dictionary
        course_id, user_id, query, suggested_pids, feedback_pid, user_rating = self._unpack_feedback(feedback)
        time = datetime.now()

        # Get the course
        course = Course.objects(course_id=course_id)

        # If it doesn't exist, return failure
        if not course:
            return False

        # Record the feedback
        feedback_record = StudentFeedbackRecord(course_id=course_id,
                                                user_id=user_id,
                                                time=time,
                                                query=query,
                                                suggested_pids=suggested_pids,
                                                feedback_pid=feedback_pid,
                                                user_rating=user_rating).save()

        return True


    def validate_feedback(self, feedback):
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

        # Extract information from dictionary
        course_id, user_id, query, suggested_pids, feedback_pid, user_rating = self._unpack_feedback(feedback)

        # Check that the user rating are within the accepted limits
        if (user_rating < self.min_rating) or (user_rating > self.max_rating):
            return False, "Rating must be between {} and {}.".format(self.min_rating, self.max_rating)

        # Check that the query string isn't empty
        if not query:
            return False, "Invalid query string."

        # Check for valid course id
        if not Course.objects(course_id=course_id):
            return False, "Course {} is currently not supported.".format(course_id)

        # Check that the feedback is for a post that was actually recommended
        if feedback_pid not in suggested_pids:
            return False, "The post id {} is not in the list of suggested posts ids {}.".format(feedback_pid, suggested_pids)

        # Check that all suggested pids actually exist
        for pid in suggested_pids:
            if not Post.objects(course_id=course_id, post_id=pid):
                return False, "Post id {} does not exist for course {}".format(pid, course_id)

        return True, ""


    def _unpack_feedback(self, feedback):
        course_id      = feedback["course_id"]
        user_id        = feedback["user_id"]
        query          = feedback["query"]
        suggested_pids = feedback["suggested_pids"]
        feedback_pid   = feedback["feedback_pid"]
        user_rating    = feedback["user_rating"]

        return course_id, user_id, query, suggested_pids, feedback_pid, user_rating
