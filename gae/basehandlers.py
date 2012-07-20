import webapp2
import os
import jinja2
import json
from .utils import login_required
from google.appengine.api import users
from google.appengine.api import xmpp
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


class RegisterHandler(JsonRequestHandler):

    @login_required("NOT_AUTHORIZED")
    def post(self):
        super(RegisterHandler, self).post()

        if self.data['event'] == 'register':
            # Send invitation from push-sms@appspot.com to user's GTalk
            xmpp.send_invite(self.user.email())
            account = Account(
                key_name=self.user.email(), user=self.user,
                registration_id=self.data['registration_id'],
                phone=self.data['phone']
            )
            account.put()
            self.response.out.write('OK')
        elif self.data['event'] == 'unregister':
            account = Account.get_by_key_name(
                key_names=self.user.email()
            )
            if account.registration_id == self.data['registration_id']:
                account.delete()
                self.response.out.write('OK')


# Handle notifying the received SMS through GTalk
class HookHandler(JsonRequestHandler):

    def post(self):
        pass
