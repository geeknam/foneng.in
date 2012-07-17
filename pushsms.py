import webapp2
from gae import basehandlers, xmpp

app = webapp2.WSGIApplication([
    ('/', basehandlers.MainPage),
    ('/register', basehandlers.RegisterHandler),
    ('/unregister', basehandlers.UnregisterHandler),
    ('/_ah/xmpp/message/chat/', xmpp.XMPPHandler)
], debug=True
)
