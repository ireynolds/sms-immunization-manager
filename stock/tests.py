"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stock.apps import StockLevel, StockOut
from sim.operations import check_signal, commit_signal

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

called_fns = None

class log_if_called:
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        def log_if_called_decorated(*args, **kwargs):
            called_fns.add(self.name)
            func(*args, **kwargs)
        return log_if_called_decorated

class Namespace:
    '''Just an empty container.'''
    pass

class StockLevelTest(TestCase):
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


class StockOutTest(TestCase):
    """
    All tests involving a the StockOut app.
    """
    def send(self, fields, check=None, commit=None):
        msg = MockMessage(fields)

        ns = Namespace()

        # Called at most once
        ns.check_args = None
        ns.commit_args = None

        # Possibly called many times
        ns.responses = []

        @log_if_called('check')
        def capture_check(**kwargs): ns.check_args = kwargs
        check_signal.connect(capture_check, sender=StockOut)

        @log_if_called('commit')
        def capture_commit(**kwargs): ns.commit_args = kwargs
        commit_signal.connect(capture_commit, sender=StockOut)

        @log_if_called('respond')
        def capture_respond(response): ns.responses.append(response)
        msg.respond = capture_respond

        if check: check_signal.connect(check, sender=StockOut)
        if commit: commit_signal.connect(commit, sender=StockOut)

        so = StockOut(None)
        so.handle(msg)

        return ns

    def setUp(self):
        global called_fns
        called_fns = set()

    def assertCalled(self, *names):
        for name in names:
            self.assertIn(name, called_fns)

    def assertNotCalled(self, *names):
        for name in names:
            self.assertNotIn(name, called_fns)

    def test_handle_simple(self):
        ns = self.send({ "operations": { "SE": "A" }})
        self.assertCalled('check', 'commit', 'respond')

        # It is assumed in all other tests that check_args and commit_args have
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('stock_code', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('stock_code', ns.commit_args)

        self.assertEqual(1, len(ns.responses))

    def test_handle_one_valid_arg(self):
        ns = self.send({ "operations": { "SE": "A" }})
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual("A", ns.commit_args['stock_code'])

        self.assertEqual(1, len(ns.responses))
        self.assertIn("Thanks for your report.", ns.responses[0])

    def test_with_no_arg(self):
        ns = self.send({ "operations": { "SE": "" }})
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("Error with message. We understood everything until:", ns.responses[0])

    def test_valid_followed_by_junk(self):
        ns = self.send({ "operations": { "SE": "AW 049045" }})
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("Error with message. We understood everything until:", ns.responses[0])