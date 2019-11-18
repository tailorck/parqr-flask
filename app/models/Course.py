from app.db import db
from app.models.Post import Post


class Course(db.Document):
    cid = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    number = db.StringField(required=True)
    term = db.StringField(required=True)
