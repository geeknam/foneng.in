import webapp2
import os
import jinja2

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__), '../templates/'
    )
)


class BaseRequestHandler(webapp2.RequestHandler):

    def render(self, template, context={}):
        template = jinja_environment.get_template(template)
        self.response.out.write(template.render(context))


class MainPage(BaseRequestHandler):

    def get(self):
        self.render('index.html')


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
