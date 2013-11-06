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

class Source(db.Model):
    current_user = db.UserProperty()
    direction = db.StringProperty()
    
class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        if user:
            source_key = self.request.get('g')
            if not source_key:
                source_key = user.user_id()
                source = Source(key_name = source_key,
                            current_user = user)
                crowdee = Crowdee(user = user,
                                  source = source_key,
                                  direction = "None")
                crowdee.put()
                source.put()
            else:
                source = Source.get_by_key_name(source_key)
                crowd = Crowdee(user = user,
                                source = source_key,
                                direction = "None")
                crowd.put()
                source.put()

            if source:
                token = channel.create_channel(source_key + user.user_id())
                template_values = {'token': token,
                                   'current_user_id': user.user_id(),
                                   'source_key': source_key,
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
        SourceUpdater(source).send_update(SourceUpdater(source).get_source_message)

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
                        'user': users.get_current_user().user_id(),
                        'direction': None
                       }
        return json.dumps(sourceUpdate)

    def send_update(self, message):
        for crowdee in Crowdee.all().filter("source =", self.source.key().name()):
            if crowdee.user != users.get_current_user():
                channel.send_message(self.source.key().name() + crowdee.user.user_id(), message)
        
    def make_move(self, direction):
        sourceUpdate = None
        for crowdee in Crowdee.all().filter("source =", self.source.key().name()):
            if crowdee.user == users.get_current_user():
                sourceUpdate = {
                                'user': users.get_current_user().user_id(),
                                'direction': direction
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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

application = webapp2.WSGIApplication([
                                      ('/', MainPage),
                                      ('/opened', OpenedPage),
                                      ('/direction', MovePage),
                                      ('/getdirection', GetDirection),
                                      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
