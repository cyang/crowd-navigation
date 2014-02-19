import logging
import json
import urllib
import jinja2
import os
import webapp2

from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.api import channel

import OpenTokSDK

from config import tokbox_api_key, tokbox_api_secret
from models import Crowdee, Room

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader([os.path.dirname(__file__), os.path.dirname(__file__) + "/templates"]),
    variable_start_string="((",
    variable_end_string="))")

opentok_sdk = OpenTokSDK.OpenTokSDK(tokbox_api_key, tokbox_api_secret)

class NavPubPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('nav-pub.html')
        self.response.out.write(template.render())

class NavPub2Page(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        #Redirect the user if they aren't logged in.
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        
        #Setup tokbox tokens.
        tokbox_session_id = opentok_sdk.create_session().session_id
        tokbox_token = opentok_sdk.generate_token(tokbox_session_id)
        sub_tokbox_token = opentok_sdk.generate_token(tokbox_session_id, OpenTokSDK.RoleConstants.SUBSCRIBER)
        
        #Create the room.
        room_key = user.user_id()
        room = Room(key_name = room_key,
                        current_user = user,
                        session_id = tokbox_session_id,
                        pub_token = tokbox_token,
                        sub_token = sub_tokbox_token
                       )
        room.put()
        
        #Display the template.
        token = channel.create_channel(room_key)
        template_values = {'token': token,
                           'tokbox_api_key': tokbox_api_key,
                           'tokbox_session_id': tokbox_session_id,
                           'tokbox_token': tokbox_token,
                           'room_key': room_key,
                           'initial_message': RoomUpdater(room).get_room_message_for_room(),
                           }
        template = jinja_environment.get_template('nav-pub.html')
        self.response.out.write(template.render(template_values))
        
class NavPub2WithPlaybackPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        #Redirect the user if they aren't logged in.
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        
        #Setup tokbox tokens.
        tokbox_session_id = opentok_sdk.create_session().session_id
        tokbox_token = opentok_sdk.generate_token(tokbox_session_id)
        sub_tokbox_token = opentok_sdk.generate_token(tokbox_session_id, OpenTokSDK.RoleConstants.SUBSCRIBER)
        
        #Create the room.
        room_key = user.user_id()
        room = Room(key_name = room_key,
                        current_user = user,
                        session_id = tokbox_session_id,
                        pub_token = tokbox_token,
                        sub_token = sub_tokbox_token
                       )
        room.put()
        
        #Display the template.
        token = channel.create_channel(room_key)
        template_values = {'token': token,
                           'tokbox_api_key': tokbox_api_key,
                           'tokbox_session_id': tokbox_session_id,
                           'tokbox_token': tokbox_token,
                           'room_key': room_key,
                           'initial_message': RoomUpdater(room).get_room_message_for_room(),
                           }
        template = jinja_environment.get_template('nav-pub-with-playback.html')
        self.response.out.write(template.render(template_values))

class RoutingPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('routing.html')
        self.response.out.write(template.render())

class VirtualRealityPubPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('vr-pub.html')
        self.response.out.write(template.render())

class VirtualRealityPubPlaybackPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('vr-pub-with-playback.html')
        self.response.out.write(template.render())

class VirtualRealityPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            room_key = "vr"
            room = Room.get_by_key_name(room_key)
            if not room:
                room = Room(key_name = room_key,
                            current_user = user)
                room.put()

            #Check if the crowdee already exists for this user and room.
            crowdeeQuery = Crowdee.all()
            crowdeeQuery.filter("user =", user)
            crowdeeQuery.filter("room =", room_key)
            crowdee = crowdeeQuery.get()
            #If the crowdee doesn't exist...
            if not crowdee:
                #Create the crowdee for the user and room.
                crowdee = Crowdee(user = user,
                                  room = room_key,
                                  channel = room_key + "_" + user.user_id(),
                                  direction = "None",
                                  weight = 1)
                crowdee.put()
            
            token = channel.create_channel(room_key + "_" + user.user_id())
            template_values = {'token': token,
                               'current_user_id': user.user_id(),
                               'room_key': room_key,
                               'weight': 1,
                               'initial_message': RoomUpdater(room).get_room_message()
                               }
            template = jinja_environment.get_template('vr-room.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class DemoPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            room_key = "demo"
            room = Room.get_by_key_name(room_key)
            if not room:
                room = Room(key_name = room_key,
                            current_user = user)
                room.put()

            #Check if the crowdee already exists for this user and room.
            crowdeeQuery = Crowdee.all()
            crowdeeQuery.filter("user =", user)
            crowdeeQuery.filter("room =", room_key)
            crowdee = crowdeeQuery.get()
            #If the crowdee doesn't exist...
            if not crowdee:
                #Create the crowdee for the user and room.
                crowdee = Crowdee(user = user,
                                  room = room_key,
                                  channel = room_key + "_" + user.user_id(),
                                  direction = "None",
                                  weight = 1)
                crowdee.put()
            
            token = channel.create_channel(room_key + "_" + user.user_id())
            template_values = {'token': token,
                               'current_user_id': user.user_id(),
                               'room_key': room_key,
                               'weight': 1,
                               'initial_message': RoomUpdater(room).get_room_message()
                               }
            template = jinja_environment.get_template('demo-room.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class NavRoomPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            room_key = self.request.get('g')
            if not room_key:
                room_key = user.user_id()
                room = Room(key_name = room_key,
                            current_user = user)
                room.put()
            else:
                room = Room.get_by_key_name(room_key)

            if room:
                #Check if the crowdee already exists for this user and room.
                crowdeeQuery = Crowdee.all()
                crowdeeQuery.filter("user =", user)
                crowdeeQuery.filter("room =", room_key)
                crowdee = crowdeeQuery.get()
                #If the crowdee doesn't exist...
                if not crowdee:
                    #Create the crowdee for the user and room.
                    crowdee = Crowdee(user = user,
                                      room = room_key,
                                      channel = room_key + "_" + user.user_id(),
                                      direction = "None",
                                      weight = 1)
                    crowdee.put()
                
                token = channel.create_channel(room_key + "_" + user.user_id())
                template_values = {'token': token,
                                   'current_user_id': user.user_id(),
                                   'room_key': room_key,
                                   'weight': 1,
                                   'initial_message': RoomUpdater(room).get_room_message()
                                   }
                #Add tokbox tokens if they exist.
                if room.session_id:
                    template_values.update({'tokbox_api_key': tokbox_api_key,
                                            'tokbox_session_id': room.session_id,
                                            'tokbox_token': room.sub_token
                                           })
                template = jinja_environment.get_template('nav-room-base.html')
                self.response.out.write(template.render(template_values))
            else:
                self.response.out.write('No such room')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class RoomPage(webapp2.RequestHandler):
    
    def get(self, room_id):
        user = users.get_current_user()

        if user:
            template = jinja_environment.get_template('nav-room-base-ng.html')
            self.response.out.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))


class HostRoomResource(webapp2.RequestHandler):
    
    def post(self):
        user = users.get_current_user()

        if not user:
            #Handle the user not being logged in. TODO
            return
        
        #Setup tokbox tokens.
        tokbox_session_id = opentok_sdk.create_session().session_id
        tokbox_token = opentok_sdk.generate_token(tokbox_session_id)
        sub_tokbox_token = opentok_sdk.generate_token(tokbox_session_id, OpenTokSDK.RoleConstants.SUBSCRIBER)
        
        #Create the room.
        room_key = user.user_id()
        room = Room(key_name = room_key,
                    current_user = user,
                    session_id = tokbox_session_id,
                    pub_token = tokbox_token,
                    sub_token = sub_tokbox_token
                   )
        room.put()
        
        #Create the channel token.
        token = channel.create_channel(room_key)
        
        #Respond with room information.
        room_data = {'token': token,
                     'tokbox_api_key': tokbox_api_key,
                     'tokbox_session_id': tokbox_session_id,
                     'tokbox_token': tokbox_token,
                     'room_key': room_key,
                     'initial_message': RoomUpdater(room).get_room_message_for_room(),
                    }
        self.response.out.write(json.dumps(room_data))


class CrowdeeRoomResource(webapp2.RequestHandler):
    
    def put(self, room_key):
        user = users.get_current_user()

        if not user:
            #Handle the user not being logged in. TODO
            return
        
        #Get the room.
        room = Room.get_by_key_name(room_key)

        if not room:
            #Handle the room not existing.
            return
        
        #Check if the crowdee already exists for this user and room.
        crowdeeQuery = Crowdee.all()
        crowdeeQuery.filter("user =", user)
        crowdeeQuery.filter("room =", room_key)
        crowdee = crowdeeQuery.get()
        #If the crowdee doesn't exist...
        if not crowdee:
            #Create the crowdee for the user and room.
            crowdee = Crowdee(user = user,
                              room = room_key,
                              channel = room_key + "_" + user.user_id(),
                              direction = "None",
                              weight = 1)
            crowdee.put()
        
        token = channel.create_channel(room_key + "_" + user.user_id())
        
        #Compile the crowdee data.
        crowdee_data = {
                        'channel_token': token,
                        'user_id': user.user_id(),
                        'user_name': user.nickname(),
                        'room_key': room_key,
                        'user_weight': 1,
                        'tokbox_api_key': tokbox_api_key,
                        'tokbox_session_id': room.session_id,
                        'tokbox_token': room.sub_token,
                       }
        
        #Respond with the json.
        self.response.out.write(json.dumps(crowdee_data))


class OpenedPage(webapp2.RequestHandler):
    def post(self):
        room = RoomFromRequest(self.request).get_room()
        RoomUpdater(room).get_existing_state()

class OpenedRoomPage(webapp2.RequestHandler):
    def post(self):
        room = RoomFromRequest(self.request).get_room()
        RoomUpdater(room).get_existing_state_for_room()

class RoomFromRequest():
    room = None

    def __init__(self, request):
        user = users.get_current_user()
        room_key = request.get('g')
        if user and room_key:
            self.room = Room.get_by_key_name(room_key)

    def get_room(self):
        return self.room
    
class MovePage(webapp2.RequestHandler):

    def post(self):
        room = RoomFromRequest(self.request).get_room()
        user = users.get_current_user()
        direction = self.request.get('d')
        if room and user:
            RoomUpdater(room).make_move(direction)

class RoomUpdater():
    room = None

    def __init__(self, room):
        self.room = room
        
    def get_room_message(self):
        roomUpdate = {
                        'user_id': users.get_current_user().user_id(),
                        'name': "None",
                        'direction': None,
                        'weight': 1
                       }
        return json.dumps(roomUpdate)
    
    def get_room_message_for_room(self):
        roomUpdate = {
                        'initialize': True
                       }
        return json.dumps(roomUpdate)
    
    def get_existing_state(self):
        for crowdee in Crowdee.all().filter("room =", self.room.key().name()):
            if crowdee.user != users.get_current_user() and crowdee.direction != "None":
                message = json.dumps({
                                      'user_id': crowdee.user.user_id(),
                                      'name': crowdee.user.nickname(),
                                      'direction': crowdee.direction,
                                      'weight': crowdee.weight
                                    })
                channel.send_message(self.room.key().name() + "_" + users.get_current_user().user_id(), message)
    
    def get_existing_state_for_room(self):
        if self.room:
            for crowdee in Crowdee.all().filter("room =", self.room.key().name()):
                if crowdee.user != users.get_current_user() and crowdee.direction != "None":
                    message = json.dumps({
                                          'user_id': crowdee.user.user_id(),
                                          'name': crowdee.user.nickname(),
                                          'direction': crowdee.direction,
                                          'weight': crowdee.weight
                                        })
                    channel.send_message(self.room.key().name(), message)

    def send_update(self, message):
        channel.send_message(self.room.key().name(), message)
        for crowdee in Crowdee.all().filter("room =", self.room.key().name()):
            if crowdee.user != users.get_current_user():
                channel.send_message(self.room.key().name() + "_" + crowdee.user.user_id(), message)
        
    def make_move(self, direction):
        roomUpdate = None
        aggregate = "Nothing"
        maximum = 0
        crowd_size = 0
        direction_list = {"Forward": 0, "Right": 0, "Left": 0, "Stop": 0}
        for crowdee in Crowdee.all().filter("room =", self.room.key().name()):
            if crowdee.user == users.get_current_user():
                crowdee.direction = direction
                crowdee.put()
                roomUpdate = {
                                'user_id': users.get_current_user().user_id(),
                                'name': crowdee.user.nickname(),
                                'direction': direction,
                                'weight': crowdee.weight
                               }
            if crowdee.direction and crowdee.direction != None and crowdee.direction != "None" and crowdee.direction != "Nothing":
                direction_list[crowdee.direction] += 1
                crowd_size += 1
        if not roomUpdate:
            logging.error("make_move failed: code 1")
            return
        for d in direction_list.keys():
            if direction_list[d] > maximum:
                maximum = direction_list[d]
                aggregate = d
        self.room.direction = aggregate
        self.room.put()
        #If the room if the VR, post the aggregate to the VR server.
        if self.room.key().name() == "vr":
            if crowd_size != 0:
                speed = maximum / float(crowd_size)
            else:
                speed = 0
            url = "http://ccvcl.org/~khoo/posttome.php"
            form_fields = {"direction": aggregate, "speed": speed, "crowd_size":crowd_size}
            form_data = urllib.urlencode(form_fields)
            urlfetch.fetch(url=url,
                    payload=form_data,
                    method=urlfetch.POST)

        self.send_update(json.dumps(roomUpdate))
        
    def delete_move(self, user_id):
        aggregate = "Nothing"
        maximum = 0
        crowd_size = 0
        direction_list = {"Forward": 0, "Right": 0, "Left": 0, "Stop": 0}
        for crowdee in Crowdee.all().filter("room =", self.room.key().name()):
            if crowdee.direction and crowdee.direction != None and crowdee.direction != "None" and crowdee.direction != "Nothing":
                direction_list[crowdee.direction] += 1
                crowd_size += 1
        for d in direction_list.keys():
            if direction_list[d] > maximum:
                maximum = direction_list[d]
                aggregate = d
        self.room.direction = aggregate
        self.room.put()
        #If the room if the VR, post the aggregate to the VR server.
        if self.room.key().name() == "vr":
            if crowd_size != 0:
                speed = maximum / crowd_size
            else:
                speed = 0
            url = "http://ccvcl.org/~khoo/posttome.php"
            form_fields = {"direction": aggregate, "speed": speed, "crowd_size":crowd_size}
            form_data = urllib.urlencode(form_fields)
            urlfetch.fetch(url=url,
                    payload=form_data,
                    method=urlfetch.POST)
        roomUpdate = {
                           'user_id': user_id,
                           'delete': True
                       }
        self.send_update(json.dumps(roomUpdate))
        
class GetDirection(webapp2.RequestHandler):
    def get(self):
        #self.response.out.write("400")
        room = Room.all()
        direction = "None"
        for s in room:
            if(s.direction):
                direction = s.direction
        self.response.out.write(direction)
        #direction = Room.all().fetch(1).direction()
        #return direction
        
class GetDemoDirection(webapp2.RequestHandler):
    def get(self):
        room = Room.get_by_key_name("demo")
        direction = "None"
        if(room.direction):
            direction = room.direction
        self.response.out.write(direction)

class ChannelDisconnect(webapp2.RequestHandler):
    def post(self):
        channel_token = self.request.get('from')
        user_crowd = Crowdee.all().filter("channel =", channel_token)
        #Although there should only be one user, it will still be received as a list.
        for user_crowdee in user_crowd:
            room = Room.get_by_key_name(user_crowdee.room)
            user_id = user_crowdee.user.user_id()
            user_crowdee.delete()
            if room:
                RoomUpdater(room).delete_move(user_id)

class ChannelConnect(webapp2.RequestHandler):
    def post(self):
        return
