from .basehandlers import JsonRequestHandler
from .utils import login_required


class NewMessageHandler(JsonRequestHandler):

    @login_required()
    def post(self):
        pass
