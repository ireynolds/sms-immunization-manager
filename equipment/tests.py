"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from apps import EquipmentFailure
import operation_parser.app
from sim.operations import commit_signal, check_signal

class MockMessage: 
    """
    A useful class that satisfies the basic interface of a RapidSMS Message.
    """
    def __init__(self, text):
        self.text = text
        self.fields = {}

class EquipmentFailureTest(TestCase):

    def call_and_capture(self, text, check=None, commit=None, respond=None):
        if check:
            check_signal.connect(check, sender=EquipmentFailure)
        if commit:
            commit_signal.connect(commit, sender=EquipmentFailure)

        msg = MockMessage(text)
        if respond:
            msg.respond = lambda response: respond(response)
        else:
            msg.respond = lambda response: None

        op = operation_parser.app.OperationParser(None)
        op.parse(msg)

        ff = EquipmentFailure(None)
        ff.handle(msg)

    def test_handle(self):
        def check(**kwargs):
            callbacks['check'] = True

        def commit(**kwargs):
            callbacks['commit'] = True

        def respond(response):
            callbacks['respond'] = True

        # None have been called yet
        callbacks = {
            'check': False,
            'commit': False,
            'respond': False 
        }

        self.call_and_capture("NF A B", commit=commit, check=check, respond=respond)

        self.assertTrue(callbacks['check'], "check was not called")
        self.assertTrue(callbacks['commit'], "commit was not called")
        self.assertTrue(callbacks['respond'], "respond was not called")
