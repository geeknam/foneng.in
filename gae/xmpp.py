from google.appengine.ext.webapp import xmpp_handlers
from models import Account

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
        message_key = account.reply_to_last(message.arg)

        gcm = GCM(API_KEY)
        gcm.plaintext_request(
            registration_id=account.registration_id,
            data={'key': message_key},
            collapse_key=str(message_key)
        )

    def sms_command(self, message=None):
        idx_email = message.sender.index('/')
        email = message.sender[0:idx_email]
        idx_phone = message.arg.index(':')
        phone = message.arg[0:idx_phone]
        content = unicode(message.arg[idx_phone + 1:])

        # Get the account
        account = Account.get_by_key_name(
            key_names=email
        )
        message_key = self.account.send_message_to(
            phones=[phone], content=content
        )

        gcm = GCM(API_KEY)
        gcm.plaintext_request(
            registration_id=account.registration_id,
            data={'key': message_key},
            collapse_key=str(message_key)
        )

        message.reply("SMS has been sent to: %s" % phone)

    def who_command(self, message=None):
        idx_email = message.sender.index('/')
        email = message.sender[0:idx_email]

        # Get the account
        account = Account.get_by_key_name(
            key_names=email
        )
        contacts = account.search_contacts(message.arg)

        reply = ''
        if contacts:
            for c in contacts:
                reply += c + '\n'

        message.reply(reply)

    def help_command(self, message=None):
        pass
