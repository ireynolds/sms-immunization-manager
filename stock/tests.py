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
        check_signal.connect(capture_check, sender=StockLevel)

        @log_if_called('commit')
        def capture_commit(**kwargs): ns.commit_args = kwargs
        commit_signal.connect(capture_commit, sender=StockLevel)

        @log_if_called('respond')
        def capture_respond(response): ns.responses.append(response)
        msg.respond = capture_respond

        if check: check_signal.connect(check, sender=StockLevel)
        if commit: commit_signal.connect(commit, sender=StockLevel)

        so = StockLevel(None)
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
        ns = self.send({ "operations": { "SL": "A1" }})
        self.assertCalled('check', 'commit')

        # It is assumed in all other tests that check_args and commit_args have
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('stock_levels', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('stock_levels', ns.commit_args)


    def test_valid_single_char_stock_code(self):
        ns = self.send({ "operations": { "SL": "A1" }})
        self.assertCalled('check', 'commit')

        self.assertEqual(ns.commit_args['stock_levels']["A"], 1)

    def test_valid_multiple_char_stock_code(self):
        ns = self.send({ "operations": { "SL": "AB1" }})
        self.assertCalled('check', 'commit')

        self.assertEqual(ns.commit_args['stock_levels']["AB"], 1)

    def test_valid_multiple_char_stock_code(self):
        ns = self.send({ "operations": { "SL": "ABC12" }})
        self.assertCalled('check', 'commit')

        self.assertEqual(ns.commit_args['stock_levels']["ABC"], 12)

    def test_valid_multiple_stock_codes(self):
        ns = self.send({ "operations": { "SL": "ABC12E3fG63H4" }})
        self.assertCalled('check', 'commit')

        self.assertEqual(ns.commit_args['stock_levels']["ABC"], 12)
        self.assertEqual(ns.commit_args['stock_levels']["E"], 3)
        self.assertEqual(ns.commit_args['stock_levels']["fG"], 63)
        self.assertEqual(ns.commit_args['stock_levels']["H"], 4)

    def test_valid_multiple_stock_codes_spaces(self):
        ns = self.send({ "operations": { "SL": "ABC12 E3 fG6" }})
        self.assertCalled('check', 'commit')

        self.assertEqual(ns.commit_args['stock_levels']["ABC"], 12)
        self.assertEqual(ns.commit_args['stock_levels']["E"], 3)
        self.assertEqual(ns.commit_args['stock_levels']["fG"], 6)

    def test_missing_stock_code(self):
        ns = self.send({ "operations": { "SL": "42" }})
        self.assertNotCalled('check', 'commit')

    def test_missing_stock_level(self):
        ns = self.send({ "operations": { "SL": "A6B" }})
        self.assertNotCalled('check', 'commit')

    def test_error_from_commit(self):
        # TODO:
        pass


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
        self.assertCalled('check', 'commit')

        # It is assumed in all other tests that check_args and commit_args have
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('stock_code', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('stock_code', ns.commit_args)

    def test_handle_one_valid_arg(self):
        ns = self.send({ "operations": { "SE": "A" }})
        self.assertCalled('check', 'commit')

        self.assertEqual(ns.commit_args['stock_code'], "A")

    def test_with_no_arg(self):
        ns = self.send({ "operations": { "SE": "" }})
        self.assertNotCalled('check', 'commit')

        self.assertIn("Error with message. We understood everything until:", ns.responses[0])

    def test_valid_followed_by_junk(self):
        ns = self.send({ "operations": { "SE": "AW 049045" }})
        self.assertNotCalled('check', 'commit')

        self.assertIn("Error with message. We understood everything until:", ns.responses[0])

    def test_with_no_arg_followed_by_junk(self):
        ns = self.send({ "operations": { "SE": "93489384" }})
        self.assertNotCalled('check', 'commit')

        self.assertIn("Error with message. We understood everything until:", ns.responses[0])