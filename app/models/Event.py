from app.db import db
# from app.models.EventData import EventData


class Event(db.Document):
    time = db.DateTimeField(required=True)
    event_type = db.StringField(required=True)
    event_name = db.StringField(required=True)
    user_id = db.StringField(required=True)
    # event_data = db.EmbeddedDocumentField(EventData, default=EventData,
    #                                       required=True)
    course_id = db.StringField(required=True)
    event_data = db.DictField()
