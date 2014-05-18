"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stock.apps import StockLevel, StockOut
from utils.operations import semantic_signal, commit_signal
from random import randint

class StockAppTest(TestCase):
    def setUp(self):
        sl = StockLevel(None)
        self.OP_CODE = sl.get_opcodes().pop()

class StockLevelTest(StockAppTest):
    """
    All tests involving a the StockLevel app.
    """
    def test_handle_simple(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, "A1", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['A'], 1)

    def test_valid_single_char_stock_code(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, "A 1", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['A'], 1)

    def test_valid_multiple_char_stock_code(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, "AB1", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['AB'], 1)

    def test_valid_multiple_char_stock_code(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, "ABC 12", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['ABC'], 12)

    def test_valid_multiple_stock_codes(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, "ABC12E3FG63H4", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['ABC'], 12)
        self.assertEqual(kwargs['stock_levels']['E'], 3)
        self.assertEqual(kwargs['stock_levels']['FG'], 63)
        self.assertEqual(kwargs['stock_levels']['H'], 4)

    def test_valid_multiple_stock_codes_spaces(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, "ABC12 E 3 FG 63H4", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_levels']['ABC'], 12)
        self.assertEqual(kwargs['stock_levels']['E'], 3)
        self.assertEqual(kwargs['stock_levels']['FG'], 63)
        self.assertEqual(kwargs['stock_levels']['H'], 4)

    def test_missing_stock_code(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, "42", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_missing_stock_level(self):
        sl = StockLevel(None)
        effects, kwargs = sl.parse_arguments(self.OP_CODE, " A  6 B", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

class StockOutTest(StockAppTest):
    """
    All tests involving a the StockOut app.
    """
    def test_valid(self):
        se = StockOut(None)
        effects, kwargs = se.parse_arguments(self.OP_CODE, " A", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['stock_out'], 'A')

    def test_error_no_arg(self):
        se = StockOut(None)
        effects, kwargs = se.parse_arguments(self.OP_CODE, "  ", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_valid_followed_by_junk(self):
        se = StockOut(None)
        effects, kwargs = se.parse_arguments(self.OP_CODE, "AW049045", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_junk_only(self):
        se = StockOut(None)
        effects, kwargs = se.parse_arguments(self.OP_CODE, "934><8,.984", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')