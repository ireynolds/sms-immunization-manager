"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from apps import Help
from utils.tests import SIMTestCase

class SimpleTest(SIMTestCase):
    
    def send_args(self, argstring):
        return Help(None).parse_arguments("NF", argstring, None)

    def test_delims_before(self):
        effects, args = self.send_args(" ;, SL")

        self.assertNotEqual(None, args)
        self.assertIn('opcode', args)
        self.assertEqual('SL', args['opcode'])

        self.assertEqual(1, len(effects))
        self.assertInfoIn(effects)

    def test_delims_after(self):
        effects, args = self.send_args("SL ;, ")

        self.assertNotEqual(None, args)
        self.assertIn('opcode', args)
        self.assertEqual('SL', args['opcode'])

        self.assertEqual(1, len(effects))
        self.assertInfoIn(effects)

    def test_no_id(self):
        effects, args = self.send_args("")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_chars_after_id(self):
        effects, args = self.send_args("SL 1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_invalid_chars_for_id(self):
        effects, args = self.send_args("SL1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_chars_after_id_nodelims(self):
        effects, args = self.send_args("SL1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_invalid_chars_for_id_nodelims(self):
        effects, args = self.send_args("1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)
