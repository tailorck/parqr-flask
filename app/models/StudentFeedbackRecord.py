from app.db import db
from app.models.Query import Query


class StudentFeedbackRecord(db.Document):
    course_id = db.StringField(required=True)
    user_id = db.StringField(required=True)
    time = db.DateTimeField(required=True)
    query_rec_pair = db.ReferenceField(Query, required=True)
    feedback_pid = db.IntField(required=True)
    user_rating = db.IntField(required=True)