"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from app import OperationParser

class MockMessage: 
    def __init__(self, text):
        # Satisfy the interface upon which OperationParser.parse depends
        self.text = text
        self.fields = {}

class SimpleTest(TestCase):
    
    ## Helpers
    
    def parse(self, text):
        # No connection -- leave it as None
        op = OperationParser(None)
        msg = MockMessage(text)
        op.parse(msg)
        return msg.fields['operations']

    def check(self, text, *expected_ops):
        expected_ops = dict(expected_ops)
        actual_ops = self.parse(text)
        self.assertEqual(expected_ops, actual_ops)

    ## Tests

    def test_recognize_opcode(self):
        self.check("SL",
            ("SL", ""))

    def test_not_split_args(self):
        self.check("SL P 100",
            ("SL", "P 100"))
