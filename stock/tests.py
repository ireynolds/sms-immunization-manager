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
        self.response = response

class StockLevelTests(TestCase):
    """
    All tests involving a the StockLevel app.
    """
    def test_single_char_stock_code(self):
        """
        Tests the parsing of a valid message containing a single character stock code.
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

    def test_multiple_char_stock_code(self):
        """
        Tests the parsing of a valid message containing a two character stock code.
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            self.stock_levels = kwargs['stock_levels']

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "AB1" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the contents of the values passed with the signal
        self.assertEqual(self.stock_levels["AB"], 1)

    def test_multiple_char_stock_code(self):
        """
        Tests the parsing of a valid message containing a three character stock code.
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            self.stock_levels = kwargs['stock_levels']

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "ABC12" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the contents of the values passed with the signal
        self.assertEqual(self.stock_levels["ABC"], 12)

    def test_multiple_stock_codes(self):
        """
        Tests the parsing of a valid message containing mutliple stock codes
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            self.stock_levels = kwargs['stock_levels']

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "ABC12E3fG6" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the contents of the values passed with the signal
        self.assertEqual(self.stock_levels["ABC"], 12)
        self.assertEqual(self.stock_levels["E"], 3)
        self.assertEqual(self.stock_levels["fG"], 6)

    def test_multiple_stock_codes_spaces(self):
        """
        Tests the parsing of a valid message containing multiple stock codes seperated by spaces.
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            self.stock_levels = kwargs['stock_levels']

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "ABC12 E3 fG6" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the contents of the values passed with the signal
        self.assertEqual(self.stock_levels["ABC"], 12)
        self.assertEqual(self.stock_levels["E"], 3)
        self.assertEqual(self.stock_levels["fG"], 6)

    def test_missing_stock_code(self):
        """
        Tests the parsing of an invalid message missing a stock code.
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            self.stock_levels = kwargs['stock_levels']

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "6" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the error message response
        self.assertEqual(self.stock_levels, {})
        self.assertEqual(msg.response, "Please try again. We understood everything until: 6")

    def test_missing_stock_level(self):
        """
        Tests the parsing of an invalid message missing a stock level.
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            self.stock_levels = kwargs['stock_levels']

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "A6B" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify the error message response
        self.assertEqual(self.stock_levels, {})
        self.assertEqual(msg.response, "Please try again. We understood everything until: B")

    def test_error_from_commit(self):
        """
        Tests the handling of an error returned from the commit phase.
        """
        self.stock_levels = {}

        def mock_listen(**kwargs):
            return "ERROR"

        # Create an instance of StockLevel
        sl = StockLevel(None)

        # Create a test message
        msg = MockMessage({ "operations": { "SL": "A6B4CD99" }})

        # Register a test listner
        check_signal.connect(mock_listen, sender=StockLevel)

        # Pass the test message to the handle method
        sl.handle(msg)

        # Verify there is an error message response
        self.assertNotEqual(msg.response, None)