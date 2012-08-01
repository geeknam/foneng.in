import unittest
from google.appengine.api import users
from google.appengine.ext import testbed
from gae.models import *


class AccountTestCase(unittest.TestCase):

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

    def test_account_email(self):
        self.assertEqual(self.account.email, 'nam@gmail.com')

    def test_get_latest_incoming(self):
        self.assertEqual(len(self.account.get_latest_incoming(5)), 0)

        IncomingMessage(account=self.account,
            content='Hello World', sender=self.contact
        ).put()

        self.assertEqual(len(self.account.get_latest_incoming(5)), 1)

    def test_get_latest_outgoing(self):
        self.assertEqual(len(self.account.get_latest_outgoing(5)), 0)

        OutgoingMessage(account=self.account,
            content='Hi there', recipients=[self.contact.key()]
        ).put()

        self.assertEqual(len(self.account.get_latest_outgoing(5)), 1)

    def test_get_latest_calls(self):
        Call(account=self.account, caller=self.contact).put()
        self.assertEqual(len(self.account.get_latest_calls(5)), 1)

    def test_get_latest_links(self):
        Link(account=self.account, url='http://google.com').put()
        self.assertEqual(len(self.account.get_latest_links(5)), 1)

    def test_search_contacts(self):
        pass

    def test_send_message_to(self):
        phones = [self.contact.phone, '56465758']
        key = self.account.send_message_to(phones, 'Group message')
        message = db.get(key)
        self.assertEqual(message.account.email, self.account.email)
        self.assertEqual(message.content, 'Group message')
        self.assertIn(self.contact.key(), message.recipients)

    def test_reply_to_last(self):
        IncomingMessage(account=self.account,
            content='Test reply', sender=self.contact
        ).put()
        key = self.account.reply_to_last('Reply to latest')
        message = db.get(key)
        self.assertEqual(message.account.email, self.account.email)
        self.assertEqual(message.content, 'Reply to latest')
        self.assertEqual(len(message.recipients), 1)
        self.assertIn(self.contact.key(), message.recipients)

    def test_receive_message_from(self):
        key = self.account.receive_message_from(
            '1234567', 'John Smith', 'Sup'
        )
        message = db.get(key)
        self.assertEqual(message.account.email, self.account.email)
        self.assertEqual(message.sender.full_name, 'John Smith')

    def test_receive_call_from(self):
        pass

    def test_send_link(self):
        pass

    def test_get_conversation_with(self):
        phones = [self.contact.phone, '56465758']
        self.account.send_message_to(phones, 'Group message')
        self.account.receive_message_from(
            '56465758', 'John Smith', 'Sup'
        )
        contact = Contact.get_by_key_name('%s:%s' % (self.account.email, '56465758'))
        conversation = self.account.get_conversation_with(contact, 20)

        self.assertEqual(len(conversation), 2)
