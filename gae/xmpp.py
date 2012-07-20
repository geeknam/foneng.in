from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext import db
from models import Account, OutgoingMessage

from gcm import GCM
from settings import API_KEY


# Handle replies from GTalk to send SMS to the latest sender
class XMPPHandler(xmpp_handlers.CommandHandler):

    def text_message(self, message):
        #Get sender's email
        idx = message.sender.index('/')
        email = message.sender[0:idx]

        # Get the latest sender's phone number
        account = Account.get_by_key_name(
            key_names=email
        )
        last_incoming = account.get_latest_incoming(1)[0]

        # Create an OutgoingMessage
        sent_message = OutgoingMessage(
            recipients=[last_incoming.sender], account=account,
            content=unicode(message.arg)
        )
        sent_message.put()

        message_key = str(db.Key.from_path(
            'Message', sent_message.key().id()
        ))
        gcm = GCM(API_KEY)
        gcm.plaintext_request(
            registration_id=account.registration_id,
            data={'key': message_key},
            collapse_key=str(message_key)
        )

    def sms_command(self, message=None):
        pass

    def help_command(self, message=None):
        pass
