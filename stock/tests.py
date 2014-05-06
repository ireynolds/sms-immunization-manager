"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stock.apps import StockLevel, StockOut
import operation_parser.app
from sim.operations import check_signal, commit_signal
from random import randint

class MockMessage:
    """
    A useful class that satisfies the interface of a RapidSMS
    Message on which StockLevel and StockOut depends.
    """
    def __init__(self, text):
        # Satisfy the interface upon which StockLevel.handle depends
        self.text = text
        self.fields = {}

called_fns = None

class log_if_called:
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        def log_if_called_decorated(*args, **kwargs):
            called_fns.add(self.name)
            return func(*args, **kwargs)
        return log_if_called_decorated

class Namespace:
    '''Just an empty container.'''
    pass

class StockLevelTest(TestCase):
    """
    All tests involving a the StockLevel app.
    """
    def send(self, text):

        msg = MockMessage(text)
        ns = Namespace()

        # Called at most once
        ns.check_args = None
        ns.commit_args = None

        # check phase listners
        @log_if_called('check')
        def capture_check_X(**kwargs):
            ns.check_args = kwargs
            if 'X' in kwargs['stock_levels']:
                return "X ERROR %d" % randint(0, 9999)

        @log_if_called('check')
        def capture_check_Y(**kwargs):
            ns.check_args = kwargs
            if 'Y' in kwargs['stock_levels']:
                return "Y ERROR %d" % randint(0, 9999)

        @log_if_called('check')
        def capture_check_Z(**kwargs):
            ns.check_args = kwargs
            if 'Z' in kwargs['stock_levels']:
                return "Z ERROR %d" % randint(0, 9999)

        # connect the check phase listners
        check_signal.connect(capture_check_X, sender=StockLevel)
        check_signal.connect(capture_check_Y, sender=StockLevel)
        check_signal.connect(capture_check_Z, sender=StockLevel)

        # commit phase listners
        @log_if_called('commit')
        def capture_commit_Q(**kwargs):
            ns.commit_args = kwargs
            if 'Q' in kwargs['stock_levels']:
                return "Q ERROR"

        @log_if_called('commit')
        def capture_commit_R(**kwargs):
            ns.commit_args = kwargs
            if 'R' in kwargs['stock_levels']:
                return "R ERROR"

        @log_if_called('commit')
        def capture_commit_S(**kwargs):
            ns.commit_args = kwargs
            if 'S' in kwargs['stock_levels']:
                return "S ERROR"

        # connect the commit phase listners
        commit_signal.connect(capture_commit_Q, sender=StockLevel)
        commit_signal.connect(capture_commit_R, sender=StockLevel)
        commit_signal.connect(capture_commit_S, sender=StockLevel)

        # parse the message
        op = operation_parser.app.OperationParser(None)
        op.parse(msg)

        # handle the message
        so = StockLevel(None)
        so.handle(msg)
        ns.errors = msg.errors

        # disconnect the signal listners
        check_signal.disconnect(capture_check_X, sender=StockLevel)
        check_signal.disconnect(capture_check_Y, sender=StockLevel)
        check_signal.disconnect(capture_check_Z, sender=StockLevel)

        commit_signal.disconnect(capture_commit_Q, sender=StockLevel)
        commit_signal.disconnect(capture_commit_R, sender=StockLevel)
        commit_signal.disconnect(capture_commit_S, sender=StockLevel)

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
        ns = self.send("SL A1")
        self.assertCalled('check', 'commit')

        # It is assumed in all other tests that check_args and commit_args have
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('stock_levels', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('stock_levels', ns.commit_args)

    def test_valid_single_char_stock_code(self):
        ns = self.send("SL A 1")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["A"], 1)

    def test_valid_multiple_char_stock_code(self):
        ns = self.send("SLAB1")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["AB"], 1)

    def test_valid_multiple_char_stock_code(self):
        ns = self.send("SL ABC 12")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["ABC"], 12)

    def test_valid_multiple_stock_codes(self):
        ns = self.send("SLAbC12E3fG63h4")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["ABC"], 12)
        self.assertEqual(ns.commit_args['stock_levels']["E"], 3)
        self.assertEqual(ns.commit_args['stock_levels']["FG"], 63)
        self.assertEqual(ns.commit_args['stock_levels']["H"], 4)

    def test_valid_multiple_stock_codes_spaces(self):
        ns = self.send("SLABC12 E 3 fG 63H4")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["ABC"], 12)
        self.assertEqual(ns.commit_args['stock_levels']["E"], 3)
        self.assertEqual(ns.commit_args['stock_levels']["FG"], 63)
        self.assertEqual(ns.commit_args['stock_levels']["H"], 4)

    def test_missing_stock_code(self):
        ns = self.send("SL 42")
        self.assertNotCalled('check', 'commit')
        self.assertEqual(len(ns.errors), 1)

    def test_missing_stock_level(self):
        ns = self.send("SL A  6 B")
        self.assertNotCalled('check', 'commit')
        self.assertEqual(len(ns.errors), 1)

    def test_1of3_error_from_check(self):
        ns = self.send("SL A1234X5BBC1D8")
        self.assertCalled('check')
        self.assertNotCalled('commit')
        self.assertEqual(ns.check_args['stock_levels']["A"], 1234)
        self.assertEqual(ns.check_args['stock_levels']["X"], 5)
        self.assertEqual(ns.check_args['stock_levels']["BBC"], 1)
        self.assertEqual(ns.check_args['stock_levels']["D"], 8)
        self.assertEqual(len(ns.errors), 1)

    def test_2of3_error_from_check(self):
        ns = self.send("SLY33 A1234 X5 BBC1")
        self.assertCalled('check')
        self.assertNotCalled('commit')
        self.assertEqual(ns.check_args['stock_levels']["Y"], 33)
        self.assertEqual(ns.check_args['stock_levels']["A"], 1234)
        self.assertEqual(ns.check_args['stock_levels']["X"], 5)
        self.assertEqual(ns.check_args['stock_levels']["BBC"], 1)
        self.assertEqual(len(ns.errors), 2)

    def test_3of3_error_from_check(self):
        ns = self.send("SL Y33 A1234 X5 BBC1Z44")
        self.assertCalled('check')
        self.assertNotCalled('commit')
        self.assertEqual(ns.check_args['stock_levels']["Y"], 33)
        self.assertEqual(ns.check_args['stock_levels']["A"], 1234)
        self.assertEqual(ns.check_args['stock_levels']["X"], 5)
        self.assertEqual(ns.check_args['stock_levels']["BBC"], 1)
        self.assertEqual(ns.check_args['stock_levels']["Z"], 44)
        self.assertEqual(len(ns.errors), 3)

    def test_1of3_error_from_commit(self):
        ns = self.send("SLQ34")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["Q"], 34)
        self.assertEqual(len(ns.errors), 1)

    def test_2of3_error_from_commit(self):
        ns = self.send("SLA23 Q34 R33")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["A"], 23)
        self.assertEqual(ns.commit_args['stock_levels']["Q"], 34)
        self.assertEqual(ns.commit_args['stock_levels']["R"], 33)
        self.assertEqual(len(ns.errors), 2)

    def test_3of3_error_from_commit(self):
        ns = self.send("SLA23 Q34 R33 BBC1S99")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_levels']["A"], 23)
        self.assertEqual(ns.commit_args['stock_levels']["Q"], 34)
        self.assertEqual(ns.commit_args['stock_levels']["R"], 33)
        self.assertEqual(ns.commit_args['stock_levels']["BBC"], 1)
        self.assertEqual(ns.commit_args['stock_levels']["S"], 99)
        self.assertEqual(len(ns.errors), 3)

class StockOutTest(TestCase):
    """
    All tests involving a the StockOut app.
    """
    def send(self, text):
        msg = MockMessage(text)
        ns = Namespace()

        # Called at most once
        ns.check_args = None
        ns.commit_args = None

        # check phase listners
        @log_if_called('check')
        def capture_check_X(**kwargs):
            ns.check_args = kwargs
            if 'X' in kwargs['stock_code']:
                return "X ERROR %d" % randint(0, 9999)

        @log_if_called('check')
        def capture_check_Y(**kwargs):
            ns.check_args = kwargs
            if 'Y' in kwargs['stock_code']:
                return "Y ERROR %d" % randint(0, 9999)

        @log_if_called('check')
        def capture_check_Z(**kwargs):
            ns.check_args = kwargs
            if 'Z' in kwargs['stock_code']:
                return "Z ERROR %d" % randint(0, 9999)

        # connect the check phase listners
        check_signal.connect(capture_check_X, sender=StockOut)
        check_signal.connect(capture_check_Y, sender=StockOut)
        check_signal.connect(capture_check_Z, sender=StockOut)

        # commit phase listners
        @log_if_called('commit')
        def capture_commit_Q(**kwargs):
            ns.commit_args = kwargs
            if 'Q' in kwargs['stock_code']:
                return "Q ERROR %d" % randint(0, 9999)

        @log_if_called('commit')
        def capture_commit_R(**kwargs):
            ns.commit_args = kwargs
            if 'R' in kwargs['stock_code']:
                return "R ERROR %d" % randint(0, 9999)

        @log_if_called('commit')
        def capture_commit_S(**kwargs):
            ns.commit_args = kwargs
            if 'S' in kwargs['stock_code']:
                return "S ERROR %d" % randint(0, 9999)

        # connect the commit phase listners
        commit_signal.connect(capture_commit_Q, sender=StockOut)
        commit_signal.connect(capture_commit_R, sender=StockOut)
        commit_signal.connect(capture_commit_S, sender=StockOut)

        # parse the message
        op = operation_parser.app.OperationParser(None)
        op.parse(msg)

        # handle the message
        so = StockOut(None)
        so.handle(msg)
        ns.errors = msg.errors

        # disconnect the listners
        check_signal.disconnect(capture_check_X, sender=StockOut)
        check_signal.disconnect(capture_check_Y, sender=StockOut)
        check_signal.disconnect(capture_check_Z, sender=StockOut)

        commit_signal.disconnect(capture_commit_Q, sender=StockOut)
        commit_signal.disconnect(capture_commit_R, sender=StockOut)
        commit_signal.disconnect(capture_commit_S, sender=StockOut)

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
        ns = self.send("SE A")
        self.assertCalled('check', 'commit')

        # It is assumed in all other tests that check_args and commit_args have
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('stock_code', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('stock_code', ns.commit_args)

    def test_handle_one_valid_arg(self):
        ns = self.send("SE A")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_code'], "A")
        self.assertEqual(len(ns.errors), 0)

    def test_with_no_arg(self):
        ns = self.send("SE")
        self.assertNotCalled('check', 'commit')
        self.assertEqual(len(ns.errors), 1)

    def test_valid_followed_by_junk(self):
        ns = self.send("SE AW049045")
        self.assertNotCalled('check', 'commit')
        self.assertEqual(len(ns.errors), 1)

    def test_junk_only(self):
        ns = self.send("SE 934><8,.984")
        self.assertNotCalled('check', 'commit')
        self.assertEqual(len(ns.errors), 1)

    def test_1of3_check_errors(self):
        ns = self.send("SE X")
        self.assertCalled('check')
        self.assertNotCalled('commit')
        self.assertEqual(ns.check_args['stock_code'], "X")
        self.assertEqual(len(ns.errors), 1)

    def test_2of3_check_errors(self):
        ns = self.send("SE XY")
        self.assertCalled('check')
        self.assertNotCalled('commit')
        self.assertEqual(ns.check_args['stock_code'], "XY")
        self.assertEqual(len(ns.errors), 2)

    def test_3of3_check_errors(self):
        ns = self.send("SE ZYX")
        self.assertCalled('check')
        self.assertNotCalled('commit')
        self.assertEqual(ns.check_args['stock_code'], "ZYX")
        self.assertEqual(len(ns.errors), 3)

    def test_1of3_commit_errors(self):
        ns = self.send("SE Q")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_code'], "Q")
        self.assertEqual(len(ns.errors), 1)

    def test_2of3_commit_errors(self):
        ns = self.send("SE QR")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_code'], "QR")
        self.assertEqual(len(ns.errors), 2)

    def test_3of3_commit_errors(self):
        ns = self.send("SE QRS")
        self.assertCalled('check', 'commit')
        self.assertEqual(ns.commit_args['stock_code'], "QRS")
        self.assertEqual(len(ns.errors), 3)