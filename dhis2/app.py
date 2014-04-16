import rapidsms
import logging
from rapidsms.apps.base import AppBase

# logger = logging.getLogger("rapidsms")

class PingPong(AppBase): #App(rapidsms.app.App):

    # def parse(self, message):
	# logger.debug("parse")
    #    print "parse"

    def handle(self, message):
        if message.text == 'hello world':
            message.respond('hello earthling!')
            return True
        return False
