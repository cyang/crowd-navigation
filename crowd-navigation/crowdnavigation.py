import logging
import os
from django.utils import simplejson
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class Source(db.Model):
    """All the data we store for a source"""
    userX = db.UserProperty()
    userO = db.UserProperty()
    board = db.StringProperty()
    moveX = db.BooleanProperty()
    winner = db.StringProperty()
    winning_board = db.StringProperty()

class SourceUpdater():
    source = None

    def __init__(self, source):
        logging.warning(source.userX.user_id())
        self.source = source

    def get_source_message(self):
        sourceUpdate = {
                      'board': self.source.board,
                      'userX': self.source.userX.user_id(),
                      'userO': '' if not self.source.userO else self.source.userO.user_id(),
                      'moveX': self.source.moveX,
                      'winner': self.source.winner,
                      'winningBoard': self.source.winning_board
                      }
        return simplejson.dumps(sourceUpdate)

    def send_update(self):
        message = self.get_source_message()
        channel.send_message(self.source.userX.user_id() + self.source.key().id_or_name(), message)
        if self.source.userO:
            channel.send_message(self.source.userO.user_id() + self.source.key().id_or_name(), message)

class SourceFromRequest():
    source = None;

    def __init__(self, request):
        user = users.get_current_user()
        source_key = request.get('g')
        if user and source_key:
            self.source = Source.get_by_key_name(source_key)

    def get_source(self):
        return self.source


class OpenedPage(webapp.RequestHandler):
    def post(self):
        source = SourceFromRequest(self.request).get_source()
        SourceUpdater(source).send_update()


class MainPage(webapp.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        """Renders the main page. When this page is shown, we create a new
        channel to push asynchronous updates to the client."""
        user = users.get_current_user()
        source_key = self.request.get('g')
        source = None
        if user:
            if not source_key:
                source_key = user.user_id()
                source = Source(key_name = source_key,
                            userX = user,
                            moveX = True,
                            board = '         ')
                source.put()
            else:
                source = Source.get_by_key_name(source_key)
                if not source.userO:
                    source.userO = user
                    source.put()

            source_link = 'http://localhost:8080/?g=' + source_key

            if source:
                token = channel.create_channel(user.user_id() + source_key)
                template_values = {'token': token,
                                   'me': user.user_id(),
                                   'source_key': source_key,
                                   'source_link': source_link,
                                   'initial_message': SourceUpdater(source).get_source_message()
                                   }
                path = os.path.join(os.path.dirname(__file__), 'index.html')

                self.response.out.write(template.render(path, template_values))
            else:
                self.response.out.write('No such source')
        else:
            self.redirect(users.create_login_url(self.request.uri))


application = webapp.WSGIApplication([
                                      ('/', MainPage),
                                      ('/opened', OpenedPage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
