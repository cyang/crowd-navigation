import logging
import jinja2
import json
import os
import webapp2
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app


class Crowdee(db.Model):
    user = db.UserProperty()
    source = db.StringProperty()
    direction = db.StringProperty()
    channel = db.StringProperty()
    weight = db.IntegerProperty()

class Source(db.Model):
    current_user = db.UserProperty()
    direction = db.StringProperty()

class DemoPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Go')

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
                source.put()

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
                template = jinja_environment.get_template('index.html')
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
    source = None;

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
        if not sourceUpdate:
            logging.error("make_move failed: code 1")
            return
        self.source.direction = direction
        self.source.put()
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

class ChannelDisconnect(webapp2.RequestHandler):
    def post(self):
        channel_token = self.request.get('from')
        user_crowd = Crowdee.all().filter("channel =", channel_token)
        for user_crowdee in user_crowd:
            temp = 5
            #user_crowdee.delete()

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

application = webapp2.WSGIApplication([
                                      ('/', MainPage),
                                      ('/opened', OpenedPage),
                                      ('/direction', MovePage),
                                      ('/getdirection', GetDirection),
                                      ('/_ah/channel/disconnected/', ChannelDisconnect),
                                      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
