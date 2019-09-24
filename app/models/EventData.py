from app.db import db


class EventData(db.EmbeddedDocument):
    course_id = db.StringField(required=True)
    post_id = db.IntField()


