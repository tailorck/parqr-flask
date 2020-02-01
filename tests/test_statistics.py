import pytest
import pandas as pd
import time
import mock

from app.exception import InvalidUsage
from app.statistics import (
    get_inst_att_needed_posts
)


@mock.patch('app.statistics.Course')
@mock.patch('app.statistics.convert_db_course_to_df')
@mock.patch('app.statistics.convert_db_posts_to_df')
@pytest.mark.skip('Disabled due to conversion to mongoengine queries')
def test_get_inst_att_needed_posts(mock_convert_db_posts_to_df,
                                   mock_convert_db_course_to_df,
                                   mock_Course,
                                   unit_test_course_df,
                                   unit_test_posts_df):
    """
    Top posts warranting instructor attention
        a) Check if the course ID is not valid
        b) Check if there is null df created after the following filtering:
            - Filter posts_df based on course_id
            - Filter posts_df based on instructor answer's absence
            - Filter posts_df based on student answer's absence
        c) Check multiple conditions on the cases of getting the best top
           posts for different scenario
    """

    # Case (a)
    number_of_posts = 5
    course_id = 'parqrrandomtest'
    mock_convert_db_posts_to_df.return_value = unit_test_posts_df
    mock_convert_db_course_to_df.return_value = unit_test_course_df
    mock_Course.objects.return_value = False
    with pytest.raises(InvalidUsage):
        top_posts = get_inst_att_needed_posts(course_id, number_of_posts)

    mock_Course.objects.return_value = True

    # Case (b)
    number_of_posts = 5
    course_id = 'jc6w44hrp9v2ki'
    mock_convert_db_posts_to_df.return_value = unit_test_posts_df
    mock_convert_db_course_to_df.return_value = unit_test_course_df
    top_posts = get_inst_att_needed_posts(course_id, number_of_posts)
    assert top_posts[4]["post_id"] == 296
    assert top_posts[2]["title"] == 'Assignment 3 Part 1 Discussion: Bayesian Network'
    assert len(top_posts[0]["properties"]) == 5
