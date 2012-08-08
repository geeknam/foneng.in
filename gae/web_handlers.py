from .basehandlers import JsonRequestHandler
from .utils import login_required


class ConversationHandler(JsonRequestHandler):

    @login_required("NOT_AUTHORIZED")
    def get(self, phone=None):
        super(ConversationHandler, self).get()

        if phone:
            contact = self.account.get_contact_by_phone(phone)
            convos = self.account.get_conversation_with(contact, 50)
        else:
            convos = self.account.conversations.order('-timestamp').fetch(50)
        convos_serialized = []

        for c in convos:
            convos_serialized.append(c.to_dict())
        # data = {'conversations': convos_serialized}
        self.render(convos_serialized)


class ContactHandler(JsonRequestHandler):

    @login_required("NOT_AUTHORIZED")
    def get(self):
        super(ContactHandler, self).get()

        contacts_serialized = []
        contacts = self.account.contacts
        for c in contacts:
            contacts_serialized.append(c.to_dict())

        self.render(contacts_serialized)


class LinkHandler(JsonRequestHandler):

    @login_required("NOT_AUTHORIZED")
    def get(self):
        super(LinkHandler, self).get()

        links_serialized = []
        links = self.account.links
        for l in links:
            links_serialized.append(l.to_dict())

        self.render(links_serialized)
