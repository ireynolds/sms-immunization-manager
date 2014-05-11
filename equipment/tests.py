"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from apps import EquipmentRepaired, EquipmentFailure, FridgeTemperature
import operation_parser.app
from sim.operations import commit_signal, semantic_signal
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

        @receiver(semantic_signal, sender=sender, weak=False)
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

        if check: semantic_signal.connect(check, sender=sender, weak=False)
        if commit: commit_signal.connect(commit, sender=sender, weak=False)

        op = operation_parser.app.OperationParser(None)
        op.parse(msg)

        ff = sender(None)
        ff.handle(msg)

        semantic_signal.disconnect(capture_check)
        if check: semantic_signal.disconnect(check)
        commit_signal.disconnect(capture_commit)
        if commit: commit_signal.disconnect(commit)

        return ns

    def parse(self, text):
        msg = APITest.MockMessage(text)
        sender = self.__class__.sender

        op = operation_parser.app.OperationParser(None)
        op.parse(msg)

        app = sender(None)

        # Examine each operation in the message to determine if it should be parsed
        for index in xrange(len(message.fields["operations"])):
            opcode, argstring = message.fields["operations"][index]
            if opcode in app.get_opcode():
                return self.parse_arguments(argstring, message)

class FridgeTemperatureTest(APITest):

    def test_parse_args_valid_single_zero(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("0", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events'][None], (0, 0))

    def test_parse_args_valid_two_events(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("1 2", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events'][None], (1, 2))

    def test_parse_args_valid_standard(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("A 1 0", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (1, 0))

    def test_parse_args_valid_multiple(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("A 1 0B21", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (1, 0))
        self.assertEqual(kwargs['fridge_events']['B'], (2, 1))

    def test_parse_args_valid_multiple_mix(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("A 1 0B0C43", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (1, 0))
        self.assertEqual(kwargs['fridge_events']['B'], (0, 0))
        self.assertEqual(kwargs['fridge_events']['C'], (4, 3))

    def test_parse_args_multiple_mix_valid(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments(" A 0 B 0 1 C 3 4 D 0", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['fridge_events']['A'], (0, 0))
        self.assertEqual(kwargs['fridge_events']['B'], (0, 1))
        self.assertEqual(kwargs['fridge_events']['C'], (3, 4))
        self.assertEqual(kwargs['fridge_events']['D'], (0, 0))

    def test_parse_args_error_non_zero(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("1", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_extra(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("134", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_missing_events(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("A", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_multiple_missing_events(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("A0 B", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_multiple_missing_event(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("A0 B1", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_extra_event(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("A134", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_parse_args_error_standard_extra_tag(self):
        ft = FridgeTemperature(None)
        effects, kwargs = ft.parse_arguments("AD13", None)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')