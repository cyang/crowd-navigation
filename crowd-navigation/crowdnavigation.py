import webapp2

import controllers

application = webapp2.WSGIApplication([
                                      ('/', controllers.RoutingPage),
                                      ('/main', controllers.MainPage),
                                      ('/demo', controllers.DemoPage),
                                      ('/tokbox_qs_sub', controllers.TokBoxQuickStartSubPage),
                                      ('/vr-pub', controllers.VirtualRealityPubPage),
                                      ('/nav-pub', controllers.NavPubPage),
                                      ('/vr_pub', controllers.OldVirtualRealityPubPage),
                                      ('/vr-pub-with-playback', controllers.VirtualRealityPubPlaybackPage),
                                      ('/vr-room', controllers.VirtualRealityPage),
                                      ('/vr_sub', controllers.VirtualRealitySubPage),
                                      ('/opened', controllers.OpenedPage),
                                      ('/direction', controllers.MovePage),
                                      ('/getdirection', controllers.GetDirection),
                                      ('/getdemodirection', controllers.GetDemoDirection),
                                      ('/get_vr_direction', controllers.GetVirtualRealityDirection),
                                      ('/_ah/channel/disconnected/', controllers.ChannelDisconnect),
                                      ], debug=True)
