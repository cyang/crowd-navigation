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
from models import Crowdee, Source

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
        
        #Setup tokbox tokens.
        tokbox_session_id = opentok_sdk.create_session().session_id
        tokbox_token = opentok_sdk.generate_token(tokbox_session_id)
        sub_tokbox_token = opentok_sdk.generate_token(tokbox_session_id, OpenTokSDK.RoleConstants.SUBSCRIBER)
        
        #Create the source.
        source_key = user.user_id()
        source = Source(key_name = source_key,
                        current_user = user,
                        session_id = tokbox_session_id,
                        pub_token = tokbox_token,
                        sub_token = sub_tokbox_token
                       )
        source.put()
        
        #Display the template.
        token = channel.create_channel(source_key)
        template_values = {'token': token,
                           'tokbox_api_key': tokbox_api_key,
                           'tokbox_session_id': tokbox_session_id,
                           'tokbox_token': tokbox_token,
                           'room_key': source_key,
                           'initial_message': SourceUpdater(source).get_source_message_for_source(),
                           }
        template = jinja_environment.get_template('nav-pub.html')
        self.response.out.write(template.render(template_values))
        
class NavPub2WithPlaybackPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        #Redirect the user if they aren't logged in.
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        
        #Setup tokbox tokens.
        tokbox_session_id = opentok_sdk.create_session().session_id
        tokbox_token = opentok_sdk.generate_token(tokbox_session_id)
        sub_tokbox_token = opentok_sdk.generate_token(tokbox_session_id, OpenTokSDK.RoleConstants.SUBSCRIBER)
        
        #Create the source.
        source_key = user.user_id()
        source = Source(key_name = source_key,
                        current_user = user,
                        session_id = tokbox_session_id,
                        pub_token = tokbox_token,
                        sub_token = sub_tokbox_token
                       )
        source.put()
        
        #Display the template.
        token = channel.create_channel(source_key)
        template_values = {'token': token,
                           'tokbox_api_key': tokbox_api_key,
                           'tokbox_session_id': tokbox_session_id,
                           'tokbox_token': tokbox_token,
                           'room_key': source_key,
                           'initial_message': SourceUpdater(source).get_source_message_for_source(),
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
            source_key = "vr"
            source = Source.get_by_key_name(source_key)
            if not source:
                source = Source(key_name = source_key,
                            current_user = user)
                source.put()

            #Check if the crowdee already exists for this user and source.
            crowdeeQuery = Crowdee.all()
            crowdeeQuery.filter("user =", user)
            crowdeeQuery.filter("source =", source_key)
            crowdee = crowdeeQuery.get()
            #If the crowdee doesn't exist...
            if not crowdee:
                #Create the crowdee for the user and source.
                crowdee = Crowdee(user = user,
                                  source = source_key,
                                  channel = source_key + "_" + user.user_id(),
                                  direction = "None",
                                  weight = 1)
                crowdee.put()
            
            token = channel.create_channel(source_key + "_" + user.user_id())
            template_values = {'token': token,
                               'current_user_id': user.user_id(),
                               'source_key': source_key,
                               'weight': 1,
                               'initial_message': SourceUpdater(source).get_source_message()
                               }
            template = jinja_environment.get_template('vr-room.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class DemoPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            source_key = "demo"
            source = Source.get_by_key_name(source_key)
            if not source:
                source = Source(key_name = source_key,
                            current_user = user)
                source.put()

            #Check if the crowdee already exists for this user and source.
            crowdeeQuery = Crowdee.all()
            crowdeeQuery.filter("user =", user)
            crowdeeQuery.filter("source =", source_key)
            crowdee = crowdeeQuery.get()
            #If the crowdee doesn't exist...
            if not crowdee:
                #Create the crowdee for the user and source.
                crowdee = Crowdee(user = user,
                                  source = source_key,
                                  channel = source_key + "_" + user.user_id(),
                                  direction = "None",
                                  weight = 1)
                crowdee.put()
            
            token = channel.create_channel(source_key + "_" + user.user_id())
            template_values = {'token': token,
                               'current_user_id': user.user_id(),
                               'source_key': source_key,
                               'weight': 1,
                               'initial_message': SourceUpdater(source).get_source_message()
                               }
            template = jinja_environment.get_template('demo-room.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class NavRoomPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            source_key = self.request.get('g')
            if not source_key:
                source_key = user.user_id()
                source = Source(key_name = source_key,
                            current_user = user)
                source.put()
            else:
                source = Source.get_by_key_name(source_key)

            if source:
                #Check if the crowdee already exists for this user and source.
                crowdeeQuery = Crowdee.all()
                crowdeeQuery.filter("user =", user)
                crowdeeQuery.filter("source =", source_key)
                crowdee = crowdeeQuery.get()
                #If the crowdee doesn't exist...
                if not crowdee:
                    #Create the crowdee for the user and source.
                    crowdee = Crowdee(user = user,
                                      source = source_key,
                                      channel = source_key + "_" + user.user_id(),
                                      direction = "None",
                                      weight = 1)
                    crowdee.put()
                
                token = channel.create_channel(source_key + "_" + user.user_id())
                template_values = {'token': token,
                                   'current_user_id': user.user_id(),
                                   'source_key': source_key,
                                   'weight': 1,
                                   'initial_message': SourceUpdater(source).get_source_message()
                                   }
                #Add tokbox tokens if they exist.
                if source.session_id:
                    template_values.update({'tokbox_api_key': tokbox_api_key,
                                            'tokbox_session_id': source.session_id,
                                            'tokbox_token': source.sub_token
                                           })
                template = jinja_environment.get_template('nav-room-base.html')
                self.response.out.write(template.render(template_values))
            else:
                self.response.out.write('No such source')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class OpenedPage(webapp2.RequestHandler):
    def post(self):
        source = SourceFromRequest(self.request).get_source()
        SourceUpdater(source).get_existing_state()

class OpenedSourcePage(webapp2.RequestHandler):
    def post(self):
        source = SourceFromRequest(self.request).get_source()
        SourceUpdater(source).get_existing_state_for_source()

class SourceFromRequest():
    source = None

    def __init__(self, request):
        user = users.get_current_user()
        source_key = request.get('g')
        if user and source_key:
            self.source = Source.get_by_key_name(source_key)

    def get_source(self):
        return self.source
    
class MovePage(webapp2.RequestHandler):

    def post(self):
        source = SourceFromRequest(self.request).get_source()
        user = users.get_current_user()
        direction = self.request.get('d')
        if source and user:
            SourceUpdater(source).make_move(direction)

class SourceUpdater():
    source = None

    def __init__(self, source):
        self.source = source
        
    def get_source_message(self):
        sourceUpdate = {
                        'user_id': users.get_current_user().user_id(),
                        'name': "None",
                        'direction': None,
                        'weight': 1
                       }
        return json.dumps(sourceUpdate)
    
    def get_source_message_for_source(self):
        sourceUpdate = {
                        'initialize': True
                       }
        return json.dumps(sourceUpdate)
    
    def get_existing_state(self):
        for crowdee in Crowdee.all().filter("source =", self.source.key().name()):
            if crowdee.user != users.get_current_user() and crowdee.direction != "None":
                message = json.dumps({
                                      'user_id': crowdee.user.user_id(),
                                      'name': crowdee.user.nickname(),
                                      'direction': crowdee.direction,
                                      'weight': crowdee.weight
                                    })
                channel.send_message(self.source.key().name() + "_" + users.get_current_user().user_id(), message)
    
    def get_existing_state_for_source(self):
        if self.source:
            for crowdee in Crowdee.all().filter("source =", self.source.key().name()):
                if crowdee.user != users.get_current_user() and crowdee.direction != "None":
                    message = json.dumps({
                                          'user_id': crowdee.user.user_id(),
                                          'name': crowdee.user.nickname(),
                                          'direction': crowdee.direction,
                                          'weight': crowdee.weight
                                        })
                    channel.send_message(self.source.key().name(), message)

    def send_update(self, message):
        channel.send_message(self.source.key().name(), message)
        for crowdee in Crowdee.all().filter("source =", self.source.key().name()):
            if crowdee.user != users.get_current_user():
                channel.send_message(self.source.key().name() + "_" + crowdee.user.user_id(), message)
        
    def make_move(self, direction):
        sourceUpdate = None
        aggregate = "Nothing"
        maximum = 0
        crowd_size = 0
        direction_list = {"Forward": 0, "Right": 0, "Left": 0, "Stop": 0}
        for crowdee in Crowdee.all().filter("source =", self.source.key().name()):
            if crowdee.user == users.get_current_user():
                crowdee.direction = direction
                crowdee.put()
                sourceUpdate = {
                                'user_id': users.get_current_user().user_id(),
                                'name': crowdee.user.nickname(),
                                'direction': direction,
                                'weight': crowdee.weight
                               }
            if crowdee.direction and crowdee.direction != None and crowdee.direction != "None" and crowdee.direction != "Nothing":
                direction_list[crowdee.direction] += 1
                crowd_size += 1
        if not sourceUpdate:
            logging.error("make_move failed: code 1")
            return
        for d in direction_list.keys():
            if direction_list[d] > maximum:
                maximum = direction_list[d]
                aggregate = d
        self.source.direction = aggregate
        self.source.put()
        #If the source if the VR, post the aggregate to the VR server.
        if self.source.key().name() == "vr":
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

        self.send_update(json.dumps(sourceUpdate))
        
    def delete_move(self, user_id):
        aggregate = "Nothing"
        maximum = 0
        crowd_size = 0
        direction_list = {"Forward": 0, "Right": 0, "Left": 0, "Stop": 0}
        for crowdee in Crowdee.all().filter("source =", self.source.key().name()):
            if crowdee.direction and crowdee.direction != None and crowdee.direction != "None" and crowdee.direction != "Nothing":
                direction_list[crowdee.direction] += 1
                crowd_size += 1
        for d in direction_list.keys():
            if direction_list[d] > maximum:
                maximum = direction_list[d]
                aggregate = d
        self.source.direction = aggregate
        self.source.put()
        #If the source if the VR, post the aggregate to the VR server.
        if self.source.key().name() == "vr":
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
        sourceUpdate = {
                           'user_id': user_id,
                           'delete': True
                       }
        self.send_update(json.dumps(sourceUpdate))
        
class GetDirection(webapp2.RequestHandler):
    def get(self):
        #self.response.out.write("400")
        source = Source.all()
        direction = "None"
        for s in source:
            if(s.direction):
                direction = s.direction
        self.response.out.write(direction)
        #direction = Source.all().fetch(1).direction()
        #return direction
        
class GetDemoDirection(webapp2.RequestHandler):
    def get(self):
        source = Source.get_by_key_name("demo")
        direction = "None"
        if(source.direction):
            direction = source.direction
        self.response.out.write(direction)

class ChannelDisconnect(webapp2.RequestHandler):
    def post(self):
        channel_token = self.request.get('from')
        user_crowd = Crowdee.all().filter("channel =", channel_token)
        #Although there should only be one user, it will still be received as a list.
        for user_crowdee in user_crowd:
            source = Source.get_by_key_name(user_crowdee.source)
            user_id = user_crowdee.user.user_id()
            user_crowdee.delete()
            if source:
                SourceUpdater(source).delete_move(user_id)

class ChannelConnect(webapp2.RequestHandler):
    def post(self):
        return
