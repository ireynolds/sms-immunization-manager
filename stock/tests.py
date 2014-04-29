"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stock.apps import StockLevel, StockOut
from sim.operations import check_signal


class MockMessage:
    """
    A useful class that satisfies the interface of a RapidSMS
    Message on which StockLevel and StockOut depends.
    """
    def __init__(self, fields):
        # Satisfy the interface upon which StockLevel.handle depends
        self.fields = {}

class MockListner:
    """
    A class to help test the passing of values via a signal.
    """
    def mock_listen(message, **kwargs):
        self.message = message
        self.stock_levels = kwargs

class SingleStockTests(TestCase):
    """
    All tests involving a message with a single stock code
    """
    def test_single_char_stock_code(self):
        """
        Tests the parsing of a valid message containing a single character stock code () and level
        """
        print "IN A TEST"

        ml = MockListner()

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SO", "A1" }})

        # Register a test listner
        check_signal.connect(ml.mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the contents of the values passed with the signal
        self.assertEqual(ml.message, "A1")
        self.assertEqual(ml.stock_levels["A"], 1)