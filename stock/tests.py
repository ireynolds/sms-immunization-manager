"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stock.apps import StockLevel, StockOut
from utils.operations import semantic_signal, commit_signal
from random import randint

class StockLevelTest(TestCase):
    """
    All tests involving a the StockLevel app.
    """
    def setUp(self):
        self.sl = StockLevel(None)
        self.OP_CODE = self.sl.get_opcodes().pop()

    def send_args(self, arg_string):
        return self.sl.parse_arguments(self.OP_CODE, arg_string, None)

    def test_handle_simple(self):
        effects, kwargs = self.send_args("A1")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['A'], 1)

    def test_valid_single_char_stock_code(self):
        effects, kwargs = self.send_args("A 1")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['A'], 1)

    def test_valid_multiple_char_stock_code(self):
        effects, kwargs = self.send_args("AB1")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['AB'], 1)

    def test_valid_multiple_char_stock_code(self):
        effects, kwargs = self.send_args("ABC 12")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['ABC'], 12)

    def test_valid_multiple_stock_codes(self):
        effects, kwargs = self.send_args("ABC12E3FG63H4")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['ABC'], 12)
        self.assertEqual(kwargs['stock_levels']['E'], 3)
        self.assertEqual(kwargs['stock_levels']['FG'], 63)
        self.assertEqual(kwargs['stock_levels']['H'], 4)

    def test_valid_multiple_stock_codes_spaces(self):
        effects, kwargs = self.send_args("ABC12 E 3 FG 63H4")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['ABC'], 12)
        self.assertEqual(kwargs['stock_levels']['E'], 3)
        self.assertEqual(kwargs['stock_levels']['FG'], 63)
        self.assertEqual(kwargs['stock_levels']['H'], 4)

    def test_missing_stock_code(self):
        effects, kwargs = self.send_args("42")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_missing_stock_level(self):
        effects, kwargs = self.send_args(" A  6 B")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

class StockOutTest(TestCase):
    """
    All tests involving a the StockOut app.
    """
    def setUp(self):
        self.se = StockOut(None)
        self.OP_CODE = self.se.get_opcodes().pop()

    def send_args(self, arg_string):
        return self.se.parse_arguments(self.OP_CODE, arg_string, None)

    def test_valid(self):
        effects, kwargs = self.send_args(" A")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_out'], 'A')

    def test_error_no_arg(self):
        effects, kwargs = self.send_args("  ")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_valid_followed_by_junk(self):
        effects, kwargs = self.send_args("AW049045")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_junk_only(self):
        effects, kwargs = self.send_args("934><8,.984")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')