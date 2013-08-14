import logging
import jinja2
import json
import os
import webapp2
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app


class Source(db.Model):
    current_user = db.UserProperty()

class SourceMember(db.Model):
    p_key = db.StringProperty()
    c_user = db.UserProperty()
    x_position = db.IntegerProperty()
    y_position = db.IntegerProperty()
    
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
            source = None
            source = Source.get_by_key_name(source_key)

            if source:
                sourceMember = SourceMember.get_by_key_name(user.user_id() + source_key)
                if not sourceMember:
                    sourceMember = SourceMember(key_name = user.user_id() + source_key,
                                                p_key = source.key().name(),
                                                c_user = user,
                                                x_position = None,
                                                y_position = None)
                    sourceMember.put()
                sourceMember = None
                sourceMember = SourceMember.get_by_key_name(user.user_id() + source_key)
                if sourceMember:
                    token = channel.create_channel(user.user_id() + source_key)
                    template_values = {'token': token,
                                       'current_user_id': user.user_id(),
                                       'source_key': source_key,
                                       'initial_message': SourceUpdater(source, sourceMember).get_source_message()
                                       }
                    template = jinja_environment.get_template('index.html')
                    self.response.out.write(template.render(template_values))
                else:
                    self.response.out.write('No such sourceMember')
            else:
                self.response.out.write('No such source')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class OpenedPage(webapp2.RequestHandler):
    def post(self):
        sourceMember = SourceFromRequest(self.request).get_source_member()
        source = SourceFromRequest(self.request).get_source()
        SourceUpdater(source, sourceMember).send_update()

class SourceFromRequest():
    source = None;
    sourceMember = None;

    def __init__(self, request):
        user = users.get_current_user()
        source_key = request.get('g')
        if user and source_key:
            self.sourceMember = SourceMember.get_by_key_name(user.user_id() + source_key)
            self.source = Source.get_by_key_name(source_key)

    def get_source(self):
        return self.source
    
    def get_source_member(self):
        return self.sourceMember
    
class MovePage(webapp2.RequestHandler):

    def post(self):
        source = SourceFromRequest(self.request).get_source()
        sourceMember = SourceFromRequest(self.request).get_source_member()
        user = users.get_current_user()
        if source and user:
            x_position = int(self.request.get('x'))
            y_position = int(self.request.get('y'))
            SourceUpdater(source, sourceMember).make_move(user, x_position, y_position)

class SourceUpdater():
    source = None
    sourceMember = None

    def __init__(self, source, sourceMember):
        self.source = source
        self.sourceMember = sourceMember

    def get_source_message(self):
        sourceUpdate = {
                      'c_user_id': self.sourceMember.c_user.user_id(),
                      'x_position': self.sourceMember.x_position,
                      'y_position': self.sourceMember.y_position
                      }
        return json.dumps(sourceUpdate)

    def send_update(self):
        message = self.get_source_message()
        sourceMemberList = SourceMember.all().filter("p_key", self.source.key().name())
        for sourceMember in sourceMemberList:
            channel.send_message(sourceMember.c_user.user_id() + self.source.key().id_or_name(), message)
        
    def make_move(self, user, x_position, y_position):
        self.sourceMember.x_position = x_position
        self.sourceMember.y_position = y_position
        self.sourceMember.put()
        self.send_update()


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

application = webapp2.WSGIApplication([
                                      ('/', MainPage),
                                      ('/opened', OpenedPage),
                                      ('/move', MovePage)
                                      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
