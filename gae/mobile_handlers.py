from google.appengine.ext import db
from google.appengine.api import xmpp

from .basehandlers import JsonRequestHandler
from .utils import login_required
from .models import OutgoingMessage, IncomingMessage, Contact, Account
from gcm import GCM
from settings import DEBUG, API_KEY
import logging


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


class NewMessageHandler(JsonRequestHandler):

    @login_required("NOT_AUTHORIZED")
    def post(self):
        super(NewMessageHandler, self).post()

        recipients = []
        # Loop over recipients list of phone numbers
        for r in self.data['recipients']:
            # Create or get the contact that has key_name of
            # user_email:recipient_phone and append to the list
            contact = Contact.get_or_insert(
                '%s:%s' % (self.user.email(), r.strip()),
                phone=r.strip(), account=self.account
            )
            recipients.append(contact.key())

        # Create an outgoing message and get the entity key
        sent_message = OutgoingMessage(
            recipients=recipients, account=self.account,
            content=unicode(self.data['content'])
        )
        sent_message.put()
        message_key = str(db.Key.from_path(
            'Message', sent_message.key().id()
        ))

        # Make a GCM call to phone with user's reg_id and
        # the entity key to retrieve from datastore
        if not DEBUG:
            gcm = GCM(API_KEY)
            gcm.plaintext_request(
                registration_id=self.account.registration_id,
                data={'key': message_key},
                collapse_key=str(message_key)
            )

        self.response.out.write("OK")


class FetchMessageHandler(JsonRequestHandler):

    @login_required("NOT_AUTHORIZED")
    def post(self):
        super(FetchMessageHandler, self).post()
        # Phone sends the message_key and get the whole message
        # back from datastore + mark it as sent
        om = db.get(self.data['message_key'])
        om.mark_sent()
        self.render(om.to_dict())


# Handle notifying the received SMS through GTalk
class HookHandler(JsonRequestHandler):

    def post(self):
        super(HookHandler, self).post()
        phone = self.data['phone'].strip()
        email = self.data['email'].strip()
        sender_name = self.data['full_name'].strip()
        content = unicode(self.data['content'])

        # Create or get the contact that has key_name of
        # user_email:recipient_phone and adds full_name if it's None
        contact = Contact.get_or_insert(
            '%s:%s' % (email, phone),
            phone=phone, account=self.account,
            full_name=sender_name
        )
        if not contact.full_name:
            contact.full_name = sender_name
            contact.put()

        # Create and IncomingMessage
        received_message = IncomingMessage(
            sender=contact, account=self.account,
            content=content
        )
        received_message.put()

        if not DEBUG:
            if xmpp.get_presence(email):
                msg = "%s : %s" % (sender_name, content)
                status_code = xmpp.send_message(email, msg)
                chat_message_sent = (status_code != xmpp.NO_ERROR)
            logging.debug(chat_message_sent)

        self.response.out.write("OK")
