from app.db import db
from app.models.Post import Post


class Query(db.Document):
    query = db.StringField(required=True)
