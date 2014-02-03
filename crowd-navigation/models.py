from google.appengine.ext import db

class Crowdee(db.Model):
    user = db.UserProperty()
    source = db.StringProperty()
    direction = db.StringProperty()
    channel = db.StringProperty()
    weight = db.IntegerProperty()

class Source(db.Model):
    current_user = db.UserProperty()
    direction = db.StringProperty()
    pub_token = db.StringProperty()
    sub_token = db.StringProperty()
