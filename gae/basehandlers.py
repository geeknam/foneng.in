import webapp2
import os
import jinja2
import json
from .utils import login_required
from google.appengine.api import users
from models import Account


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

    def get(self):
        self.user = users.get_current_user()
        self.account = Account.get_by_key_name(
            key_names=self.user.email()
        )

    def post(self):
        self.data = json.loads(self.request.body)
        self.user = users.get_current_user()
        self.account = Account.get_by_key_name(
            key_names=self.user.email()
        )

    def render(self, context={}):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(context))


class MainPage(BaseRequestHandler):

    def get(self):
        self.render('index.html')


class HomePage(BaseRequestHandler):

    @login_required()
    def get(self):
        self.render('index.html')
