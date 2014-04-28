"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stock.apps import StockLevel, StockOut

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class SingleStockTests(TestCase):
    """
    All tests involving a message with a single stock code
    """
    def test_single_char_stock_code(self):
        """
        Tests the parsing of a valid message containing a single character stock code () and level
        """

        # define a test signal listener
        def test_listener(message, **kwargs):
            self.message = message
            self.stock_levels = kwargs

        # Create an instance of StockLevel
        sl = StockLevel(router)

        # Create a test message
        msg = IncommingMessage(text="A1")

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the contents of the values passed with the signal
        self.assertEqual(test_listener.message, "A1")
        self.assertEqual(test_listener.stock_levels["A"], 1)

        # codes = ["A"]
        # message = "A1"
        
        # parsed = parse_stock_levels(codes, message)
        # stock_levels = parsed(0)
        # remaining = parsed(1)

        # self.assertEqual(len(remaining), 0)
        # self.assertEqual(stock_levels["A"], 1)
