import unittest
from google.appengine.api import users
from google.appengine.ext import testbed
from gae.models import *


class ConversationTestCase(unittest.TestCase):

    def setUp(self):
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

    def test_getattr(self):
        phones = [self.contact.phone]
        self.account.send_message_to(phones, 'Group message')
        conv = self.account.conversations.filter('contact =', self.contact).fetch(10)[0]
        self.assertEqual(conv.content, 'Group message')
        self.assertTrue(conv.is_outgoing)
        self.assertEqual(conv.not_exist, None)

    def test_conversation_count(self):
        phones = [self.contact.phone, '56465758']
        self.account.send_message_to(phones, 'Group message')
        self.account.receive_message_from(
            '56465758', 'John Smith', 'Sup'
        )
        sender = Contact.get_by_key_name('%s:%s' % (self.account.email, '56465758'))
        self.assertEqual(sender.full_name, 'John Smith')
        self.assertEqual(self.contact.full_name, 'John Doe')
        self.assertEqual(len(self.account.conversations.filter('contact =', sender).fetch(10)), 2)
        self.assertEqual(len(self.account.conversations.filter('contact =', self.contact).fetch(10)), 1)
