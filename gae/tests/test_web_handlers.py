import unittest
import webapp2
import json
import webtest
import os

from google.appengine.ext import testbed
from google.appengine.api import users

from gae import web_handlers
from gae.models import *


class WebHandlerTest(unittest.TestCase):
    def setUp(self):
        app = webapp2.WSGIApplication([
            ('/account/conversations/(.*)', web_handlers.ConversationHandler),
            ('/account/contacts', web_handlers.ContactHandler),
            ('/account/links', web_handlers.LinkHandler),
        ])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        new_user = users.User(email='nam@gmail.com')
        self.account = Account(user=new_user,
            phone='657657868', registration_id='234354657'
        )
        self.account.put()

        self.contact = Contact.get_or_insert(
            '%s:%s' % (self.account.email, '465475687'), account=self.account,
            phone='465475687', full_name='John Doe'
        )
        self.contact.put()

    def tearDown(self):
        self.account.delete()
        self.contact.delete()
        self.testbed.deactivate()

    def login_as_user(self, email, user_id, is_admin=False):
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def test_contact_handler(self):
        # self.account.send_message_to([self.contact.phone], 'To contact')
        # self.account.receive_message_from(
        #     self.contact.phone, self.contact.full_name, 'From contact'
        # )

        self.login_as_user(self.account.email, 'nam')

        response = self.testapp.get('/account/contacts')
        self.assertEqual(response.status_int, 200)

        parsed = json.loads(response.normal_body)
        self.assertEqual(len(parsed), 1)
