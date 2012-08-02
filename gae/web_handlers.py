from .basehandlers import JsonRequestHandler
from .utils import login_required


class AccountHandler(JsonRequestHandler):

    @login_required("NOT_AUTHORIZED")
    def get(self, phone=None):
        super(AccountHandler, self).get()

        if phone:
            contact = self.account.get_contact_by_phone(phone)
            convos = self.account.get_conversation_with(contact, 50)
        else:
            convos = self.account.conversations.fetch(50)
        convos_serialized = []

        for c in convos:
            convos_serialized.append(c.to_dict())
        self.render(convos_serialized)
