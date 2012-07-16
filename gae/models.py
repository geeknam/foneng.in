from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class UserData(db.Model):

    user = db.UserProperty(required=True)
    phone = db.PhoneNumberProperty()
    registration_time = db.DateTimeProperty(auto_now_add=True)
    registration_id = db.StringProperty(required=True)

    def get_latest_incoming(self, limit):
        return self.messages.filter(
            'class =', 'IncomingMessage'
        ).order('-time_sent').fetch(limit)

    def get_latest_outgoing(self, limit):
        return self.messages.filter(
            'class =', 'OutgoingMessage'
        ).order('-time_sent').fetch(limit)


class Contact(db.Model):

    user = db.ReferenceProperty(UserData, collection_name="contacts")
    phone = db.PhoneNumberProperty(required=True)
    full_name = db.StringProperty()


class Message(polymodel.PolyModel):

    user = db.ReferenceProperty(UserData, collection_name="messages")
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

    recipients = db.ListProperty(Contact)
    sent = db.BooleanProperty(default=False)


class IncomingMessage(Message):

    sender = db.ReferenceProperty(Contact, collection_name="sent_messages")
    received = db.BooleanProperty(default=False)
