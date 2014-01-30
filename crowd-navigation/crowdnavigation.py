import webapp2

import controllers

application = webapp2.WSGIApplication([
                                      ('/', controllers.RoutingPage),
                                      ('/main', controllers.MainPage),
                                      ('/demo', controllers.DemoPage),
                                      ('/vr-pub', controllers.VirtualRealityPubPage),
                                      ('/nav-pub', controllers.NavPubPage),
                                      ('/vr-pub-with-playback', controllers.VirtualRealityPubPlaybackPage),
                                      ('/vr-room', controllers.VirtualRealityPage),
                                      ('/vr_sub', controllers.VirtualRealitySubPage),
                                      ('/opened', controllers.OpenedPage),
                                      ('/direction', controllers.MovePage),
                                      ('/getdirection', controllers.GetDirection),
                                      ('/getdemodirection', controllers.GetDemoDirection),
                                      ('/_ah/channel/disconnected/', controllers.ChannelDisconnect),
                                      ], debug=True)
