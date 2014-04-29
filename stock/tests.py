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
        self.fields = fields

    def respond(self, response):
        #TODO: something else
        self.respnse = respnse

class SingleStockTests(TestCase):
    """
    All tests involving a message with a single stock code
    """
    def test_single_char_stock_code(self):
        """
        Tests the parsing of a valid message containing a single character stock code () and level
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            self.stock_levels = kwargs['stock_levels']

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "A1" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the contents of the values passed with the signal
        self.assertEqual(self.stock_levels["A"], 1)