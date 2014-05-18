"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from apps import Help, help_semantic, help_commit
from utils.tests import SIMTestCase
from django.conf import settings

class HelpAPITest(SIMTestCase):
    
    def send_args(self, argstring):
        return Help(None).parse_arguments("NF", argstring, None)

    def test_delims_before(self):
        effects, args = self.send_args(" ;, SL")

        self.assertNotEqual(None, args)
        self.assertIn('requested_opcode', args)
        self.assertEqual('SL', args['requested_opcode'])

        self.assertEqual(1, len(effects))
        self.assertInfoIn(effects)

    def test_delims_after(self):
        effects, args = self.send_args("SL ;, ")

        self.assertNotEqual(None, args)
        self.assertIn('requested_opcode', args)
        self.assertEqual('SL', args['requested_opcode'])

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

class HelpSemanticsTest(SIMTestCase):
    
    def send_args(self, requested_opcode):
        return help_semantic(None, None, "HE", requested_opcode)

    def test_valid_opcode(self):
        effects = self.send_args("HE")

        self.assertInfoIn(effects)

    def test_invalid_opcode(self):
        effects = self.send_args("ZZ")

        self.assertErrorIn(effects)

class HelpCommitTest(SIMTestCase):

    def send_args(self, requested_opcode):
        return help_commit(None, None, "HE", requested_opcode)

    def test_valid_opcode(self):
        effects = self.send_args("HE")
        self.assertUrgentIn(effects)

    def test_all_opcodes(self):
        for opcode in settings.SIM_OPERATION_CODES.keys():
            effects = self.send_args(opcode)
            self.assertUrgentIn(effects)