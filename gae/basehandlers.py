import webapp2
import os
import jinja2
import json
from .utils import login_required


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), '../templates/')
    )
)


class BaseRequestHandler(webapp2.RequestHandler):

    def render(self, template, context={}):
        template = jinja_environment.get_template(template)
        self.response.out.write(template.render(context))


class JsonRequestHandler(webapp2.RequestHandler):

    def render(self, context={}):
        self.response.out.write(json.dumps(context))


class MainPage(BaseRequestHandler):

    def get(self):
        self.render('index.html')


class HomePage(BaseRequestHandler):

    @login_required()
    def get(self):
        self.render('index.html')


class RegisterHandler(JsonRequestHandler):

    def post(self):
        json.loads(self.request.body)


class UnregisterHandler(JsonRequestHandler):

    def post(self):
        pass


# Handle notifying the received SMS through GTalk
class HookHandler(JsonRequestHandler):

    def post(self):
        pass
