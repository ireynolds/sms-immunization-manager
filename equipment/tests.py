"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from apps import EquipmentFailure
import operation_parser.app
from sim.operations import commit_signal, check_signal

class MockMessage: 
    """
    A useful class that satisfies the basic interface of a RapidSMS Message.
    """
    def __init__(self, text):
        self.text = text
        self.fields = {}

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

class EquipmentFailureTest(TestCase):

    def send(self, text, check=None, commit=None):
        msg = MockMessage(text)

        ns = Namespace()
        
        # Called at most once
        ns.check_args = None
        ns.commit_args = None

        # Possibly called many times
        ns.responses = []

        @log_if_called('check')
        def capture_check(**kwargs): ns.check_args = kwargs
        check_signal.connect(capture_check, sender=EquipmentFailure)
            
        @log_if_called('commit')
        def capture_commit(**kwargs): ns.commit_args = kwargs
        commit_signal.connect(capture_commit, sender=EquipmentFailure)
            
        @log_if_called('respond')
        def capture_respond(response): ns.responses.append(response)
        msg.respond = capture_respond

        if check: check_signal.connect(check, sender=EquipmentFailure)
        if commit: commit_signal.connect(commit, sender=EquipmentFailure)

        op = operation_parser.app.OperationParser(None)
        op.parse(msg)

        ff = EquipmentFailure(None)
        ff.handle(msg)

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
        ns = self.send("NF A")
        self.assertCalled('check', 'commit', 'respond')

        # It is assumed in all other tests that check_args and commit_args have 
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('equipment_id', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('equipment_id', ns.commit_args)

        self.assertEqual(1, len(ns.responses))

    def test_handle_one_valid_arg(self):
        ns = self.send("NF A")
        
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual("A", ns.commit_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_no_arg(self):
        ns = self.send("NF")
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual(None, ns.check_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_two_valid_args(self):
        ns = self.send("NF A B")
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])
    
    def test_one_invalid_arg(self):
        ns = self.send('NF Q')
        self.assertNotCalled('commit')
        self.assertCalled('check', 'respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])

    def test_valid_followed_by_junk(self):
        ns = self.send('NF A001')
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])