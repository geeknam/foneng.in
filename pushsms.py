import webapp2
from gae import handlers, xmpp

app = webapp2.WSGIApplication([
    ('/', handlers.MainPage),
    ('/register', handlers.RegisterHandler),
    ('/unregister', handlers.UnregisterHandler),
    ('/_ah/xmpp/message/chat/', xmpp.XMPPHandler)
], debug=True
)
