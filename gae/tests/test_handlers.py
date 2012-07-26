import unittest
import webapp2
import json
import webtest
import os
from google.appengine.ext import testbed

from gae.mobile_handlers import *
from gae.models import *


class AppTest(unittest.TestCase):
    def setUp(self):
        app = webapp2.WSGIApplication([
            ('/account/register', RegisterHandler)
        ])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def login_as_user(self, email, user_id, is_admin=False):
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def test_register_handler(self):
        payload = {
            'event': 'register',
            'registration_id': '12345678',
            'phone': '954385945'
        }
        json_data = json.dumps(payload)
        response = self.testapp.post('/account/register', json_data)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.normal_body, 'NOT_AUTHORIZED')

        self.login_as_user('emoinrp@gmail.com', 'emoinrp')

        response = self.testapp.post('/account/register', json_data)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.normal_body, 'OK')

        account = Account.get_by_key_name(
            key_names='emoinrp@gmail.com'
        )

        self.assertEqual(account.registration_id, payload['registration_id'])
        self.assertEqual(account.phone, payload['phone'])
        self.assertEqual(account.key().name(), 'emoinrp@gmail.com')
