import webapp2
from gae import basehandlers, xmpp

app = webapp2.WSGIApplication([
    ('/', basehandlers.MainPage),
    ('/home/', basehandlers.HomePage),
    ('/_ah/xmpp/message/chat/', xmpp.XMPPHandler)
], debug=True
)
