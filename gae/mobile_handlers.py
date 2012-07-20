from .basehandlers import JsonRequestHandler
from .utils import login_required
from .models import OutgoingMessage, Contact
from google.appengine.ext import db
from gcm import GCM

from settings import DEBUG, API_KEY


class NewMessageHandler(JsonRequestHandler):

    @login_required()
    def post(self):
        super(NewMessageHandler, self).post()

        recipients = []
        for r in self.data['recipients']:
            contact = Contact.get_or_insert(
                '%s:%s' % (self.user.email(), r.strip()),
                phone=r, account=self.account
            )
            recipients.append(contact.key())

        sent_message = OutgoingMessage(
            recipients=recipients, account=self.account,
            content=unicode(self.data['content'])
        )
        sent_message.put()
        message_key = str(db.Key.from_path(
            'Message', sent_message.key().id()
        ))

        if not DEBUG:
            gcm = GCM(API_KEY)
            gcm.plaintext_request(
                registration_id=self.account.registration_id,
                data={'message_key': message_key},
                collapse_key=str(message_key)
            )

        self.render({'key': message_key})


class FetchMessageHandler(JsonRequestHandler):

    def post(self):
        super(FetchMessageHandler, self).post()
        om = db.get(self.data['message_key'])
        om.mark_sent()
        self.render(om.to_dict())
