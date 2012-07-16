from google.appengine.ext.webapp import xmpp_handlers


# Handle replies from GTalk to send SMS to the latest sender
class XMPPHandler(xmpp_handlers.CommandHandler):

    def text_message(self, message):
        pass

    def sms_command(self, message=None):
        pass

    def help_command(self, message=None):
        pass
