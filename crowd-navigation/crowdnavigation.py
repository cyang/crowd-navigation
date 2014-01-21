import logging
import jinja2
import json
import os
import webapp2
import urllib
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.api import channel
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
    
class SandBox(webapp2.RedirectHandler):
    def get(self):
        template = jinja_environment.get_template('nav-room-base.html')
        self.response.out.write(template.render())

class TokBoxQuickStartPubPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('tokbox_qs_pub.html')
        self.response.out.write(template.render())

class TokBoxQuickStartSubPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('tokbox_qs_sub.html')
        self.response.out.write(template.render())

class RoutingPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('routing.html')
        self.response.out.write(template.render())

class VirtualRealityPubPlaybackPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('vr-pub-with-playback.html')
        self.response.out.write(template.render())

class VirtualRealityPubPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('vr-pub.html')
        self.response.out.write(template.render())

class VirtualRealitySubPage(webapp2.RequestHandler):
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

class MainPage(webapp2.RequestHandler):

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

    def send_update(self, message):
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
            form_fields = {"direction": aggregate, "speed": speed}
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
            form_fields = {"direction": aggregate, "speed": speed}
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
        
class GetVirtualRealityDirection(webapp2.RequestHandler):
    def get(self):
        source = Source.get_by_key_name("vr")
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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader([os.path.dirname(__file__), os.path.dirname(__file__) + "/templates"]),
    variable_start_string="((",
    variable_end_string="))")

application = webapp2.WSGIApplication([
                                      ('/', RoutingPage),
                                      ('/main', MainPage),
                                      ('/demo', DemoPage),
                                      ('/tokbox_qs_pub', TokBoxQuickStartPubPage),
                                      ('/tokbox_qs_sub', TokBoxQuickStartSubPage),
                                      ('/vr_pub', VirtualRealityPubPage),
                                      ('/vr-pub-with-playback', VirtualRealityPubPlaybackPage),
                                      ('/vr_sub', VirtualRealitySubPage),
                                      ('/opened', OpenedPage),
                                      ('/direction', MovePage),
                                      ('/getdirection', GetDirection),
                                      ('/getdemodirection', GetDemoDirection),
                                      ('/sandbox', SandBox),
                                      ('/get_vr_direction', GetVirtualRealityDirection),
                                      ('/_ah/channel/disconnected/', ChannelDisconnect),
                                      ], debug=True)
