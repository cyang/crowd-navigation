import json

from google.appengine.ext import db

class Crowdee(db.Model):
    user = db.UserProperty()
    room = db.StringProperty()
    direction = db.StringProperty()
    channel = db.StringProperty()
    weight = db.IntegerProperty()
    active = db.BooleanProperty(default=True)
    last_modified = db.DateTimeProperty(auto_now=True)

class Room(db.Model):
    current_user = db.UserProperty()
    direction = db.StringProperty()
    session_id = db.StringProperty()
    pub_token = db.StringProperty()
    sub_token = db.StringProperty()
    active = db.BooleanProperty(default=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    
    @classmethod
    def all_basic_json(cls):
        room_list = cls.all()
        room_dict_list = []
        for room in room_list:
            room_dict_list.append(room.basic_dict())
        return json.dumps(room_dict_list)
    
    def basic_dict(self):
        if self.key().name() == "vr":
            room_basic_dict = {
                                  "host_name": "VR",
                                  "host_id": "vr",
                                  "active": self.active,
                              }
            return room_basic_dict
        if self.key().name() == "demo":
            room_basic_dict = {
                                  "host_name": "Demo",
                                  "host_id": "demo",
                                  "active": self.active,
                              }
            return room_basic_dict
        room_basic_dict = {
                              "host_name": self.current_user.nickname(),
                              "host_id": self.current_user.user_id(),
                              "active": self.active,
                          }
        return room_basic_dict