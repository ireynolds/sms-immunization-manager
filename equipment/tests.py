"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from apps import EquipmentRepaired, EquipmentFailure
import operation_parser.app
from sim.operations import commit_signal, check_signal
from django.dispatch.dispatcher import receiver

class APITest(TestCase):

    ## Internal utility classes

    class Namespace:
        pass

    class MockMessage: 
        """
        A useful class that satisfies the basic interface of a RapidSMS Message.
        """
        def __init__(self, text):
            self.text = text
            self.fields = {}

    ## Support for asserting that signal handlers were called

    def __init__(self, arg):
        TestCase.__init__(self, arg)
        self.called_fns = None

    def setUp(self):
        self.called_fns = set()

    def assertCalled(self, *names):
        for name in names:
            self.assertIn(name, self.called_fns)

    def assertNotCalled(self, *names):
        for name in names:
            self.assertNotIn(name, self.called_fns)

    class log_if_called:
        def __init__(self, name, result_set):
            self.name = name
            self.set = result_set

        def __call__(self, func):
            def log_if_called_decorated(*args, **kwargs):
                self.set.add(self.name)
                func(*args, **kwargs)
            return log_if_called_decorated

    ## Useful test methods

    def send(self, text, check=None, commit=None):
        msg = APITest.MockMessage(text)
        sender = self.__class__.sender

        ns = APITest.Namespace()
        
        # Called at most once
        ns.check_args = None
        ns.commit_args = None

        # Possibly called many times
        ns.responses = []

        @receiver(check_signal, sender=sender, weak=False)
        @self.log_if_called('check', self.called_fns)
        def capture_check(**kwargs): 
            ns.check_args = kwargs
        
        @receiver(commit_signal, sender=sender, weak=False)    
        @self.log_if_called('commit', self.called_fns)
        def capture_commit(**kwargs): 
            ns.commit_args = kwargs
            
        @self.log_if_called('respond', self.called_fns)
        def capture_respond(response): 
            ns.responses.append(response)
        msg.respond = capture_respond

        if check: check_signal.connect(check, sender=sender, weak=False)
        if commit: commit_signal.connect(commit, sender=sender, weak=False)

        op = operation_parser.app.OperationParser(None)
        op.parse(msg)

        ff = sender(None)
        ff.handle(msg)

        check_signal.disconnect(capture_check)
        if check: check_signal.disconnect(check)
        commit_signal.disconnect(capture_commit)
        if commit: commit_signal.disconnect(commit)

        return ns


class EquipmentFailureTest(APITest):
    
    sender = EquipmentFailure

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

class EquipmentRepairedTest(APITest):

    sender = EquipmentRepaired

    def test_handle_simple(self):
        ns = self.send("WO A")
        self.assertCalled('check', 'commit', 'respond')

        # It is assumed in all other tests that check_args and commit_args have 
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('equipment_id', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('equipment_id', ns.commit_args)

        self.assertEqual(1, len(ns.responses))

    def test_handle_one_valid_arg(self):
        ns = self.send("WO A")
        
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual("A", ns.commit_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_no_arg(self):
        ns = self.send("WO")
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual(None, ns.check_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_two_valid_args(self):
        ns = self.send("WO A B")
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])
    
    def test_one_invalid_arg(self):
        ns = self.send('WO Q')
        self.assertNotCalled('commit')
        self.assertCalled('check', 'respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])

    def test_valid_followed_by_junk(self):
        ns = self.send('WO A001')
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])