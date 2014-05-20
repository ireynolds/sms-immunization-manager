from django.test import TestCase
from response.app import Responder
from moderation.models import *
from rapidsms.tests.harness.router import CreateDataMixin

class MockMessage:
    def __init__(self):
        self.fields = {}
        self.fields['operation_effects'] = []

    def respond(str):
        pass

class ResponseTest(CreateDataMixin, TestCase):

    def _add_info_effect(self, message, name, desc):
        effect = info(ugettext_noop(name), {}, ugettext_noop(desc), {})
        message.fields['operation_effects'].append(effect)

    def _add_error_effect(self, message, name, desc):
        effect = error(ugettext_noop(name), {}, ugettext_noop(desc), {})
        message.fields['operation_effects'].append(effect)

    def _add_error_effect(self, message, name, desc):
        effect = error(ugettext_noop(name), {}, ugettext_noop(desc), {})
        message.fields['operation_effects'].append(effect)

    def assertResponseSent(self, effect):
        return effect.sent_as_response == True

    def assertResponseNotSent(self, effect):
        return effect.sent_as_response == False

    def setUp(self):
        self.resp = Responder(None)
        self.message = self.create_incoming_message()
        print "\nDOES THIS EVER HAPPEN?????\n"
        self.message.fields = {}
        print self.message.fields
        self.message.fields['operation_effects'] = []
        print "\n&&&&&&&&&&&&&&&&&&&&\n"
        print self.message.fields['operation_effects']
        print "\n&&&&&&&&&&&&&&&&&&&&\n"

    def test_simple(self):
        self._add_info_effect(self.message, "Info", "No errors")
        self.resp.cleanup(self.message)

        assertResponseNotSent(message.fields[operation_effects][0])
        assertResponseSent(message.fields[operation_effects][1])
