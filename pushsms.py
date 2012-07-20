import webapp2
from gae import basehandlers, xmpp
from gae import mobile_handlers

app = webapp2.WSGIApplication([
    ('/', basehandlers.MainPage),
    ('/register', basehandlers.RegisterHandler),
    ('/hook', basehandlers.HookHandler),
    ('/new_message', mobile_handlers.NewMessageHandler),
    ('/get_message', mobile_handlers.FetchMessageHandler),
    ('/_ah/xmpp/message/chat/', xmpp.XMPPHandler)
], debug=True
)
