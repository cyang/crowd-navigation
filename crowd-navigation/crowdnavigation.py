import jinja2
import json
import os
import webapp2
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class Source(db.Model):
    """All the data we store for a source"""
    current_user = db.UserProperty()
    x_position = db.IntegerProperty()
    y_position = db.IntegerProperty()

class MainPage(webapp2.RequestHandler):
    
    def get(self):
        user = users.get_current_user()

        if user:
            source = Source(
                            key_name = 'test',
                            current_user = user,
                            x_position = None,
                            y_position = None
                            )
            source.put()
            token = channel.create_channel(user.user_id())
            template_values = {'token': token,
                               'current_user': user.user_id(),
                               'initial_message': SourceUpdater(source).get_source_message()
                               }
            #template = jinja_environment.get_template('index.html')
            #self.response.out.write(template.render(template_values))
            
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class OpenedPage(webapp2.RequestHandler):
    def post(self):
        source = SourceFromRequest(self.request).get_source()
        SourceUpdater(source).send_update()

class SourceFromRequest():
    source = None;

    def __init__(self, request):
        user = users.get_current_user()
        source_key = request.get('sourcekey')
        if user and source_key:
            self.source = Source.get_by_key_name(source_key)

    def get_source(self):
        return self.source

class SourceUpdater():
    """Creates an object to store the source's state, and handles validating moves
    and broadcasting updates to the source."""
    source = None

    def __init__(self, source):
        self.source = source

    def send_update(self):
        message = self.get_source_message()
        channel.send_message(self.source.current_user.user_id() + self.source.key().id_or_name(), message)

    def get_source_message(self):
        # The sourceUpdate object is sent to the client to render the state of a source.
        sourceUpdate = {
            'user': self.source.current_user.user_id(),
            'x_position': self.source.x_position,
            'y_position': self.source.y_position
        }
        return json.dumps(sourceUpdate)


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

application = webapp2.WSGIApplication([
                                       ('/', MainPage),
                                       ('/opened', OpenedPage)
                                       ], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
