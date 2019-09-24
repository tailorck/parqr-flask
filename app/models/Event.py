from app.db import db
from app.models import EventData

class Event(db.Document):
    event_type = db.StringField(required=True)
    event_name = db.StringField(required=True)
    time = db.DateTimeField(required=True)
    user_id = db.StringField(required=True)
    event_data = db.EmbeddedDocumentField(EventData, default=EventData,
                                          required=True)
