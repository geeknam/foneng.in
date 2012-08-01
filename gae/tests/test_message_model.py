import unittest
from google.appengine.api import users
from google.appengine.ext import testbed
from gae.models import *


class MessageTestCase(unittest.TestCase):

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

    def test_type(self):
        imessage = IncomingMessage(account=self.account,
            content='Hello World', sender=self.contact
        )
        imessage.put()
        omessage = OutgoingMessage(account=self.account,
            content='Hi there', recipients=[self.contact.key()]
        )
        omessage.put()
        self.assertTrue(imessage.type == 'incoming')
        self.assertTrue(omessage.type == 'outgoing')

    def test_is_incoming(self):
        message = IncomingMessage(account=self.account,
            content='Hello World', sender=self.contact
        )
        message.put()
        self.assertTrue(message.is_incoming)
        self.assertFalse(message.is_outgoing)

    def test_is_outgoing(self):
        message = OutgoingMessage(account=self.account,
            content='Hi there', recipients=[self.contact.key()]
        )
        message.put()
        self.assertFalse(message.is_incoming)
        self.assertTrue(message.is_outgoing)

    def test_get_not_sent(self):
        OutgoingMessage(account=self.account,
            content='Not sent', recipients=[self.contact.key()]
        ).put()
        OutgoingMessage(account=self.account, sent=True,
            content='Sent', recipients=[self.contact.key()]
        ).put()

        not_sent = OutgoingMessage.get_not_sent()
        self.assertEqual(len(list(not_sent)), 1)

        for o in not_sent:
            self.assertFalse(o.sent)

    def test_mark_sent(self):
        message = OutgoingMessage(account=self.account,
            content='Hi there', recipients=[self.contact.key()]
        )
        message.put()
        self.assertFalse(message.sent)
        message.mark_sent()
        self.assertTrue(message.sent)
