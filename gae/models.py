from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class Account(db.Model):

    user = db.UserProperty(required=True)
    phone = db.PhoneNumberProperty()
    registration_time = db.DateTimeProperty(auto_now_add=True)
    registration_id = db.StringProperty(required=True)
    store_contacts = db.BooleanProperty(default=True)
    store_messages = db.BooleanProperty(default=True)

    @property
    def email(self):
        return self.user.email()

    def get_latest_incoming(self, limit):
        return self.messages.filter(
            'class =', 'IncomingMessage'
        ).order('-time_sent').fetch(limit)

    def get_latest_outgoing(self, limit):
        return self.messages.filter(
            'class =', 'OutgoingMessage'
        ).order('-time_sent').fetch(limit)


class Contact(db.Model):

    account = db.ReferenceProperty(Account, collection_name="contacts")
    phone = db.PhoneNumberProperty(required=True)
    full_name = db.StringProperty(default="")


class Message(polymodel.PolyModel):

    account = db.ReferenceProperty(Account, collection_name="messages")
    content = db.TextProperty(required=True)
    time_sent = db.TimeProperty(auto_now_add=True)

    @property
    def type(self):
        return self.class_name().lower().strip('message')

    @property
    def is_incoming(self):
        return self.type == 'incoming'

    @property
    def is_outgoing(self):
        return self.type == 'outgoing'


class OutgoingMessage(Message):

    recipients = db.ListProperty(db.Key)
    sent = db.BooleanProperty(default=False)

    def mark_sent(self):
        if self.account.store_contacts:
            self.sent = True
            self.put()
        else:
            self.delete()

    def to_dict(self):
        recipients = [Contact.get(r).phone for r in self.recipients]

        return {
            'email': self.account.email,
            'content': self.content,
            'recipients': recipients,
        }


class IncomingMessage(Message):

    sender = db.ReferenceProperty(Contact, collection_name="sent_messages")
    received = db.BooleanProperty(default=False)

    def to_dict(self):
        return {
            'email': self.account.email,
            'content': self.content,
            'sender': self.sender.full_name,
        }


class Call(db.Model):

    account = db.ReferenceProperty(Account, collection_name="calls")
    caller = db.ReferenceProperty(Contact, collection_name="calls")
    time_called = db.TimeProperty(auto_now_add=True)
