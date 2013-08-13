import jinja2
import simplejson
import os
import webapp2
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app


class Source(db.Model):
    """All the data we store for a source"""
    user = db.UserProperty()
    x_position = db.IntegerProperty()
    y_position = db.IntegerProperty()

class MainPage(webapp2.RequestHandler):
    
    
    def get(self):
        user = users.get_current_user()

        if user:
            token = channel.create_channel(user.user_id())
            template_values = {'token': token,
                               'me': user.user_id(),
                               }
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
class MovePage(webapp2.RequestHandler):

    def post(self):
        source = SourceFromRequest(self.request).get_source()
        user = users.get_current_user()
        if source and user:
            id = int(self.request.get('i'))
            SourceUpdater(source).make_move(id, user)
      
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

    def get_source_message(self):
        # The sourceUpdate object is sent to the client to render the state of a source.
        sourceUpdate = {
            'user': self.source.current_user.user_id(),
            'x_position': self.source.x_position,
            'y_position': self.source.y_position
        }
        return simplejson.dumps(sourceUpdate)

    def send_update(self):
        message = self.get_source_message()
        channel.send_message(self.source.userX.user_id() + self.source.key().name(), message)
        if self.source.userO:
            channel.send_message(self.source.userO.user_id() + self.source.key().name(), message)

    def make_move(self, position, user):
        if position >= 0 and user == self.source.userX or user == self.source.userO:
            if self.source.moveX == (user == self.source.userX):
                boardList = list(self.source.board)
            if (boardList[position] == ' '):
                boardList[position] = 'X' if self.source.moveX else 'O'
                self.source.board = "".join(boardList)
                self.source.moveX = not self.source.moveX
                self.check_win()
                self.source.put()
                self.send_update()
                return


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

application = webapp2.WSGIApplication([('/', MainPage)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
