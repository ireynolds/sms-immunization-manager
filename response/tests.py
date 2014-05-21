from django.test import TestCase
from response.app import Responder
from moderation.models import *
from rapidsms.tests.harness.router import CreateDataMixin
from rapidsms.contrib.messagelog.app import MessageLogApp
from rapidsms.log.mixin import LoggerMixin

PLACEHOLDER_GROUP_SENDS_RESPONSE = "AAA"
PLACEHOLDER_GROUP_NO_RESPONSE = "BBB"

def add_info_effect(message, name, desc, stage=SYNTAX):
    effect = info(ugettext_noop(name), {}, ugettext_noop(desc), {})
    complete_effect(effect, message.logger_msg, stage)
    message.fields['operation_effects'].append(effect)

def add_error_effect(message, name, desc, stage=SYNTAX):
    effect = error(ugettext_noop(name), {}, ugettext_noop(desc), {})
    complete_effect(effect, message.logger_msg, stage)
    message.fields['operation_effects'].append(effect)

def add_urgent_effect(message, name, desc, stage=SYNTAX):
    effect = urgent(ugettext_noop(name), {}, ugettext_noop(desc), {})
    complete_effect(effect, message.logger_msg, stage)
    message.fields['operation_effects'].append(effect)

class ResponseTest(CreateDataMixin, TestCase):

    def assertResponseSent(self, effect):
        self.assertEqual(effect.sent_as_response, True)

    def assertResponseNotSent(self, effect):
        self.assertEqual(effect.sent_as_response, False)

    def assertNumEffects(self, message, n):
        self.assertEqual(len(message.fields['operation_effects']), n)

    def setUp(self):
        self.resp = Responder(None)

    def createMessage(self):
        msgLogger = MessageLogApp(None)
        resp = Responder(None)
        message = self.create_incoming_message()
        msgLogger.parse(message)

        message.fields = {}
        message.fields['operation_effects'] = []
        message.fields['group'] = PLACEHOLDER_GROUP_SENDS_RESPONSE

        return message

    def test_simple(self):
        message = self.createMessage()
        add_info_effect(message, "Info", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 2)
        self.assertResponseNotSent(message.fields['operation_effects'][0])
        self.assertResponseSent(message.fields['operation_effects'][1])

    def test_multiple_effects_no_errors(self):
        message = self.createMessage()
        add_info_effect(message, "Info1", "No errors")
        add_info_effect(message, "Info2", "No errors")
        add_info_effect(message, "Info3", "No errors")
        add_info_effect(message, "Info4", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 5)
        for i in range(4):
            self.assertResponseNotSent(message.fields['operation_effects'][i])
        self.assertResponseSent(message.fields['operation_effects'][4])

    def test_multiple_effects_one_error_first(self):
        message = self.createMessage()
        add_error_effect(message, "Error", "Big Errors")
        add_info_effect(message, "Info2", "No errors")
        add_info_effect(message, "Info3", "No errors")
        add_info_effect(message, "Info4", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 4)
        self.assertResponseSent(message.fields['operation_effects'][0])
        for i in range(1, 4):
            self.assertResponseNotSent(message.fields['operation_effects'][i])

    def test_multiple_effects_one_errors_mid(self):
        message = self.createMessage()
        add_info_effect(message, "Info1", "No errors")
        add_info_effect(message, "Info2", "No errors")
        add_error_effect(message, "Error", "Big Errors")
        add_info_effect(message, "Info4", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 4)
        self.assertResponseNotSent(message.fields['operation_effects'][0])
        self.assertResponseNotSent(message.fields['operation_effects'][1])
        self.assertResponseSent(message.fields['operation_effects'][2])
        self.assertResponseNotSent(message.fields['operation_effects'][3])

    def test_multiple_effects_one_errors_last(self):
        message = self.createMessage()
        add_info_effect(message, "Info1", "No errors")
        add_info_effect(message, "Info2", "No errors")
        add_info_effect(message, "Info3", "No errors")
        add_error_effect(message, "Error", "Big errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 4)
        for i in range(3):
            self.assertResponseNotSent(message.fields['operation_effects'][i])
        self.assertResponseSent(message.fields['operation_effects'][3])

    def test_multiple_errors(self):
        message = self.createMessage()
        add_info_effect(message, "Info1", "No errors")
        add_error_effect(message, "Error1", "Big errors")
        add_error_effect(message, "Error2", "Big errors")
        add_info_effect(message, "Info2", "No errors")
        add_error_effect(message, "Error3", "Big errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 5)
        self.assertResponseNotSent(message.fields['operation_effects'][0])
        self.assertResponseSent(message.fields['operation_effects'][1])
        self.assertResponseNotSent(message.fields['operation_effects'][2])
        self.assertResponseNotSent(message.fields['operation_effects'][3])
        self.assertResponseNotSent(message.fields['operation_effects'][4])

    def test_one_urgent_no_errors_with_confirm(self):
        message = self.createMessage()
        add_info_effect(message, "Info1", "No errors")
        add_urgent_effect(message, "Urgent", "No errors")
        add_info_effect(message, "Info2", "No errors")
        add_info_effect(message, "Info3", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 5)
        self.assertResponseNotSent(message.fields['operation_effects'][0])
        self.assertResponseSent(message.fields['operation_effects'][1])
        self.assertResponseNotSent(message.fields['operation_effects'][2])
        self.assertResponseNotSent(message.fields['operation_effects'][3])
        self.assertResponseSent(message.fields['operation_effects'][4])

    def test_multiple_urgent_no_errors_with_confirm(self):
        message = self.createMessage()
        add_info_effect(message, "Info1", "No errors")
        add_urgent_effect(message, "Urgent1", "No errors")
        add_urgent_effect(message, "Urgent2", "No errors")
        add_urgent_effect(message, "Urgent3", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 5)
        self.assertResponseNotSent(message.fields['operation_effects'][0])
        for i in range(1, 5):
            self.assertResponseSent(message.fields['operation_effects'][i])

    def test_one_urgent_no_errors_no_confirm(self):
        message = self.createMessage()
        message.fields['group'] = PLACEHOLDER_GROUP_NO_RESPONSE
        add_info_effect(message, "Info1", "No errors")
        add_urgent_effect(message, "Urgent", "No errors")
        add_info_effect(message, "Info2", "No errors")
        add_info_effect(message, "Info3", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 4)
        self.assertResponseNotSent(message.fields['operation_effects'][0])
        self.assertResponseSent(message.fields['operation_effects'][1])
        self.assertResponseNotSent(message.fields['operation_effects'][2])
        self.assertResponseNotSent(message.fields['operation_effects'][3])

    def test_multiple_urgent_no_errors_no_confirm(self):
        message = self.createMessage()
        message.fields['group'] = PLACEHOLDER_GROUP_NO_RESPONSE
        add_info_effect(message, "Info1", "No errors")
        add_urgent_effect(message, "Urgent1", "No errors")
        add_urgent_effect(message, "Urgent2", "No errors")
        add_urgent_effect(message, "Urgent3", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 4)
        self.assertResponseNotSent(message.fields['operation_effects'][0])
        for i in range(1, 4):
            self.assertResponseSent(message.fields['operation_effects'][i])

    def test_no_errors_no_confirm(self):
        message = self.createMessage()
        message.fields['group'] = PLACEHOLDER_GROUP_NO_RESPONSE
        add_info_effect(message, "Info1", "No errors")
        add_info_effect(message, "Info2", "No errors")
        add_info_effect(message, "Info3", "No errors")
        add_info_effect(message, "Info4", "No errors")
        self.resp.cleanup(message)

        self.assertNumEffects(message, 4)
        for i in range(1, 4):
            self.assertResponseNotSent(message.fields['operation_effects'][i])