import webapp2
from gae import mobile_handlers

app = webapp2.WSGIApplication([
    ('/account/register', mobile_handlers.RegisterHandler),
    ('/account/hook', mobile_handlers.HookHandler),
    ('/account/new_resource', mobile_handlers.NewResourceHandler),
    ('/account/get_resource', mobile_handlers.FetchResourceHandler),
], debug=True
)
