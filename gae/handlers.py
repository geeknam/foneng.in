import webapp2
from os import path
from google.appengine.ext.webapp.template import render


class MainPage(webapp2.RequestHandler):

    def get(self):
        tmpl = path.join(path.dirname(__file__), 'static/html/index.html')
        self.response.out.write(render(tmpl, None))


class RegisterHandler(webapp2.RequestHandler):

    def post(self):
        pass


class UnregisterHandler(webapp2.RequestHandler):

    def post(self):
        pass


# Handle notifying the received SMS through GTalk
class PushHandler(webapp2.RequestHandler):

    def post(self):
        pass
