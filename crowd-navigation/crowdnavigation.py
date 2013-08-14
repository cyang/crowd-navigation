import logging
import os
from django.utils import simplejson
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class Game(db.Model):
    """All the data we store for a game"""
    userX = db.UserProperty()
    userO = db.UserProperty()
    board = db.StringProperty()
    moveX = db.BooleanProperty()
    winner = db.StringProperty()
    winning_board = db.StringProperty()

class GameUpdater():
    game = None

    def __init__(self, game):
        logging.warning(game.userX.user_id())
        self.game = game

    def get_game_message(self):
        gameUpdate = {
                      'board': self.game.board,
                      'userX': self.game.userX.user_id(),
                      'userO': '' if not self.game.userO else self.game.userO.user_id(),
                      'moveX': self.game.moveX,
                      'winner': self.game.winner,
                      'winningBoard': self.game.winning_board
                      }
        return simplejson.dumps(gameUpdate)

    def send_update(self):
        message = self.get_game_message()
        channel.send_message(self.game.userX.user_id() + self.game.key().id_or_name(), message)
        if self.game.userO:
            channel.send_message(self.game.userO.user_id() + self.game.key().id_or_name(), message)

class GameFromRequest():
    game = None;

    def __init__(self, request):
        user = users.get_current_user()
        game_key = request.get('g')
        if user and game_key:
            self.game = Game.get_by_key_name(game_key)

    def get_game(self):
        return self.game


class OpenedPage(webapp.RequestHandler):
    def post(self):
        game = GameFromRequest(self.request).get_game()
        GameUpdater(game).send_update()


class MainPage(webapp.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        """Renders the main page. When this page is shown, we create a new
        channel to push asynchronous updates to the client."""
        user = users.get_current_user()
        game_key = self.request.get('g')
        game = None
        if user:
            if not game_key:
                game_key = user.user_id()
                game = Game(key_name = game_key,
                            userX = user,
                            moveX = True,
                            board = '         ')
                game.put()
            else:
                game = Game.get_by_key_name(game_key)
                if not game.userO:
                    game.userO = user
                    game.put()

            game_link = 'http://localhost:8080/?g=' + game_key

            if game:
                token = channel.create_channel(user.user_id() + game_key)
                template_values = {'token': token,
                                   'me': user.user_id(),
                                   'game_key': game_key,
                                   'game_link': game_link,
                                   'initial_message': GameUpdater(game).get_game_message()
                                   }
                path = os.path.join(os.path.dirname(__file__), 'index.html')

                self.response.out.write(template.render(path, template_values))
            else:
                self.response.out.write('No such game')
        else:
            self.redirect(users.create_login_url(self.request.uri))


application = webapp.WSGIApplication([
                                      ('/', MainPage),
                                      ('/opened', OpenedPage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
