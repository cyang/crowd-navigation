import webapp2
import os

import controllers

debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

application = webapp2.WSGIApplication([
                                      ('/', controllers.RoutingPage),
                                      ('/nav-room', controllers.NavRoomPage),
                                      ('/nav-pub2', controllers.NavPub2Page),
                                      ('/nav-pub2-with-playback', controllers.NavPub2WithPlaybackPage),
                                      ('/demo', controllers.DemoPage),
                                      ('/vr-pub', controllers.VirtualRealityPubPage),
                                      ('/nav-pub', controllers.NavPubPage),
                                      ('/vr-pub-with-playback', controllers.VirtualRealityPubPlaybackPage),
                                      ('/vr-room', controllers.VirtualRealityPage),
                                      ('/room/(\d+)', controllers.RoomPage),
                                      ('/opened', controllers.OpenedPage),
                                      ('/opened-room', controllers.OpenedRoomPage),
                                      ('/direction', controllers.MovePage),
                                      ('/getdirection', controllers.GetDirection),
                                      ('/getdemodirection', controllers.GetDemoDirection),
                                      ('/_ah/channel/disconnected/', controllers.ChannelDisconnect),
                                      ('/_ah/channel/connected/', controllers.ChannelConnect),
                                      ], debug=debug)
