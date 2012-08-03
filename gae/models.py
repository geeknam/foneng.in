from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import memcache


class Account(db.Model):

    user = db.UserProperty(required=True)
    phone = db.PhoneNumberProperty()
    registration_id = db.StringProperty(required=True)
    registration_time = db.DateTimeProperty(auto_now_add=True)
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

    def get_latest_calls(self, limit):
        return self.calls.order('-time_called').fetch(limit)

    def get_latest_links(self, limit):
        return self.links.order('-time_sent').fetch(limit)

    def get_contact_by_phone(self, phone):
        key_name = '%s:%s' % (self.email, phone)
        contact = memcache.get(key_name)
        if contact is not None:
            return contact
        contact = Contact.get_by_key_name(key_name)
        memcache.add(key_name, contact, 60 * 60 * 24)
        return contact

    def search_contacts(self, prefix):
        key = 'email:%s_prefix:%s' % (self.email, prefix)
        contacts = memcache.get(key)
        if contacts is not None:
            return contacts
        contacts = self.contacts.filter('full_name >=', prefix).filter(
            'full_name <', prefix + u'\ufffd'
        )
        memcache.add(key, contacts, 60 * 60 * 24)
        return contacts

    def send_message_to(self, phones, content):
        recipients = []
        contacts = []
        for p in phones:
            contact = Contact.get_or_insert(
                '%s:%s' % (self.email, p.strip()),
                phone=p.strip(), account=self
            )
            contacts.append(contact)
            recipients.append(contact.key())

        sent_message = OutgoingMessage(
            recipients=recipients, account=self,
            content=unicode(content)
        )
        sent_message.put()

        # Add this message to conversation
        for c in contacts:
            Conversation(account=self,
                contact=c, message=sent_message
            ).put()

        message_key = str(db.Key.from_path(
            'Message', sent_message.key().id()
        ))

        return message_key

    def reply_to_last(self, content):
        last_incoming = self.get_latest_incoming(1)[0]

        message_key = self.send_message_to(
            [last_incoming.sender.phone], content
        )

        return message_key

    def receive_message_from(self, phone, sender, content):
        contact = Contact.get_or_insert(
            '%s:%s' % (self.email, phone),
            phone=phone, account=self,
            full_name=sender
        )
        if not contact.full_name:
            contact.full_name = sender
            contact.put()

        received_message = IncomingMessage(
            sender=contact, account=self,
            content=content
        )
        key = received_message.put()

        # Add this message to conversation
        Conversation(account=self,
            contact=contact, message=received_message
        ).put()

        return key

    def get_conversation_with(self, contact, limit=10):
        return self.conversations.filter('contact =', contact).order('-timestamp').fetch(limit)

    def receive_call_from(self, phone, sender):
        contact = Contact.get_or_insert(
            '%s:%s' % (self.email, phone),
            phone=phone, account=self,
            full_name=sender
        )
        if not contact.full_name:
            contact.full_name = sender
            contact.put()

        received_call = Call(caller=contact, account=self)
        received_call.put()

    def send_link(self, url):
        link = Link.get_or_insert(
            '%s:%s' % (self.email, url),
            url=url, account=self
        )
        link_key = str(db.Key.from_path(
            'Link', link.key().name()
        ))

        return link_key


class Contact(db.Model):

    account = db.ReferenceProperty(Account, collection_name="contacts")
    phone = db.PhoneNumberProperty(required=True)
    full_name = db.StringProperty(default="")

    def __unicode__(self):
        return "%s: %s" % (self.full_name, self.phone)

    def __eq__(self, key):
        return self.key().name() == key

    def to_dict(self):
        return {
            'full_name': self.full_name if self.full_name != "" else "Not synced",
            'phone': self.phone
        }


class Message(polymodel.PolyModel):

    account = db.ReferenceProperty(Account, collection_name="messages")
    content = db.TextProperty(required=True)
    time_sent = db.TimeProperty(auto_now_add=True)

    @property
    def type(self):
        return self.class_name().lower().replace('message', '')

    @property
    def is_incoming(self):
        return self.type == 'incoming'

    @property
    def is_outgoing(self):
        return self.type == 'outgoing'

    def to_dict(self):
        return {
            'content': self.content,
            'time_sent': self.time_sent
        }


class OutgoingMessage(Message):

    recipients = db.ListProperty(db.Key)
    sent = db.BooleanProperty(default=False)

    def __contains__(self, key):
        return key in self.recipients

    @staticmethod
    def get_not_sent():
        return OutgoingMessage.all().filter('sent', False)

    def mark_sent(self):
        if self.account.store_contacts:
            self.sent = True
            self.put()
        else:
            self.delete()

    def to_dict(self, show_source=False):
        serialized = {
            'content': self.content,
            'time_sent': self.time_sent.isoformat()
        }
        if show_source:
            recipients = [Contact.get(r).to_dict() for r in self.recipients]
            serialized.update({'recipients': recipients})
        return serialized


class IncomingMessage(Message):

    sender = db.ReferenceProperty(Contact, collection_name="sent_messages")
    received = db.BooleanProperty(default=False)

    def to_dict(self, show_source=False):
        serialized = {
            'content': self.content,
            'time_sent': self.time_sent.isoformat(),
        }
        if show_source:
            serialized.update({'sender': self.sender.full_name})
        return serialized


class Conversation(db.Model):

    account = db.ReferenceProperty(Account, collection_name="conversations")
    contact = db.ReferenceProperty(Contact, collection_name="conversations")
    message = db.ReferenceProperty(Message)
    timestamp = db.TimeProperty(auto_now_add=True)

    def __getattr__(self, attr):
        try:
            return getattr(self.message, attr)
        except AttributeError:
            return None

    def to_dict(self):
        return {
            'contact': self.contact.to_dict(),
            'message': self.message.to_dict()
        }


class Call(db.Model):

    account = db.ReferenceProperty(Account, collection_name="calls")
    caller = db.ReferenceProperty(Contact, collection_name="calls")
    time_called = db.TimeProperty(auto_now_add=True)

    def to_dict(self):
        return {
            'email': self.account.email,
            'caller': self.caller.full_name,
            'time_called': self.time_called.isoformat()
        }


class Link(db.Model):

    account = db.ReferenceProperty(Account, collection_name="links")
    url = db.LinkProperty(required=True)
    time_sent = db.TimeProperty(auto_now_add=True)

    def to_dict(self):
        return {
            'email': self.account.email,
            'url': self.url,
            'time_sent': self.time_sent.isoformat()
        }
