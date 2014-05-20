"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from apps import EquipmentRepaired, EquipmentFailure, FridgeTemperature
from moderation.models import ERROR, INFO
from utils.tests import SIMTestCase

class EquipmentTestMixin:

    def send_args(self, argstring):
        '''Overridden in mixed-in classes.'''
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

class FridgeTemperatureTest(TestCase):
    def setUp(self):
        self.ft = FridgeTemperature(None)
        self.OP_CODE = self.ft.get_opcodes().pop()

    def send_args(self, arg_string):
        return self.ft.parse_arguments(self.OP_CODE, arg_string, None)

    def test_parse_args_valid_single_zero(self):
        effects, kwargs = self.send_args("0")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events'][None], (0, 0))

    def test_parse_args_valid_two_events(self):
        effects, kwargs = self.send_args("1 2")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events'][None], (1, 2))

    def test_parse_args_valid_standard(self):
        effects, kwargs = self.send_args("A 1 0")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (1, 0))

    def test_parse_args_valid_multiple(self):
        effects, kwargs = self.send_args("A 1 0B21")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (1, 0))
        self.assertEqual(kwargs['fridge_events']['B'], (2, 1))

    def test_parse_args_valid_multiple_mix(self):
        effects, kwargs = self.send_args("A 1 0B0C43")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (1, 0))
        self.assertEqual(kwargs['fridge_events']['B'], (0, 0))
        self.assertEqual(kwargs['fridge_events']['C'], (4, 3))

    def test_parse_args_multiple_mix_valid(self):
        effects, kwargs = self.send_args(" A 0 B 0 1 C 3 4 D 0")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (0, 0))
        self.assertEqual(kwargs['fridge_events']['B'], (0, 1))
        self.assertEqual(kwargs['fridge_events']['C'], (3, 4))
        self.assertEqual(kwargs['fridge_events']['D'], (0, 0))

    def test_parse_args_error_non_zero(self):
        effects, kwargs = self.send_args("1")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_extra(self):
        effects, kwargs = self.send_args("134")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_missing_events(self):
        effects, kwargs = self.send_args("A")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_multiple_missing_events(self):
        effects, kwargs = self.send_args("A0 B")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_multiple_missing_event(self):
        effects, kwargs = self.send_args("A0 B1")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_extra_event(self):
        effects, kwargs = self.send_args("A134")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_extra_tag(self):
        effects, kwargs = self.send_args("AD13")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')