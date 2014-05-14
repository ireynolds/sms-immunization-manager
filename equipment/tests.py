"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from apps import EquipmentRepaired, EquipmentFailure
from moderation.models import ERROR, INFO
from utils.tests import SIMTestCase

class EquipmentTestMixin:

    def send_args(self, argstring):
        pass

    def test_delims_before(self):
        effects, args = self.send_args(" ;, A")

        self.assertNotEqual(None, args)
        self.assertIn('equipment_id', args)
        self.assertEqual('A', args['equipment_id'])

        self.assertEqual(1, len(effects))
        self.assertInfoIn(effects)

    def test_delims_after(self):
        effects, args = self.send_args("A ;, ")

        self.assertNotEqual(None, args)
        self.assertIn('equipment_id', args)
        self.assertEqual('A', args['equipment_id'])

        self.assertEqual(1, len(effects))
        self.assertInfoIn(effects)

    def test_no_id(self):
        effects, args = self.send_args("")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_chars_after_id(self):
        effects, args = self.send_args("A 1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_invalid_chars_for_id(self):
        effects, args = self.send_args("1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_chars_after_id_nodelims(self):
        effects, args = self.send_args("A1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

    def test_invalid_chars_for_id_nodelims(self):
        effects, args = self.send_args("1")

        self.assertEqual(None, args)

        self.assertEqual(1, len(effects))
        self.assertErrorIn(effects)

class EquipmentFailureTest(SIMTestCase, EquipmentTestMixin):
    def send_args(self, argstring):
        return EquipmentFailure(None).parse_arguments("NF", argstring, None)

class EquipmentRepairedTest(SIMTestCase, EquipmentTestMixin):
    def send_args(self, argstring):
        return EquipmentRepaired(None).parse_arguments("WO", argstring, None)
