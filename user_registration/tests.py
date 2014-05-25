"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from user_registration.apps import PreferredLanguage

class PreferredLanguageTest(TestCase):
    """
    All tests involving PL opcode
    """

    def setUp(self):
        self.pl = PreferredLanguage(None)
        self.OP_CODE = self.pl.get_opcodes().pop()

    def send_args(self, arg_string):
        return self.pl.parse_arguments(self.OP_CODE, arg_string, None)

    def test_simple(self):
        effects, kwargs = self.send_args("1")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['preferred_lang_code'], 1)
        self.assertEqual(kwargs['preferred_lang'], 'English')

    def test_extra_char(self):
        effects, kwargs = self.send_args("1 2")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_unrecognized_char(self):
        effects, kwargs = self.send_args("4")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_unrecognized_chars(self):
        effects, kwargs = self.send_args("456")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

        
        effects, kwargs = self.send_args("abc")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

