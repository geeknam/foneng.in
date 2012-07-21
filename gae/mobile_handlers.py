from google.appengine.ext import db
from google.appengine.api import xmpp

from .basehandlers import JsonRequestHandler
from .utils import login_required
from .models import Account
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

        message_key = self.account.send_message_to(
            phones=self.data['recipients'],
            content=self.data['content']
        )

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

        # Get the account
        account = Account.get_by_key_name(
            key_names=email
        )

        account.receive_from(
            phone=phone, sender=sender_name, content=content
        )

        if not DEBUG:
            if xmpp.get_presence(email):
                msg = "%s : %s" % (sender_name, content)
                status_code = xmpp.send_message(email, msg)
                chat_message_sent = (status_code != xmpp.NO_ERROR)
            logging.debug(chat_message_sent)

        self.response.out.write("OK")
