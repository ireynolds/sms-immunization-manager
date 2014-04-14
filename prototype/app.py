from rapidsms.apps.base import AppBase

class SMSParser(AppBase):
    def parse(self, msg):
      print "PARSE"
    def handle(self, msg):
      print "HANDLE"