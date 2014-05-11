import mock
from django.test import TestCase
from operations import OperationBase, semantic_signal, commit_signal
from moderation.models import *
from django.utils.translation import ugettext_noop as _
from rapidsms.tests.harness.router import CustomRouterMixin
from rapidsms.router.blocking import BlockingRouter
from operation_parser.app import OperationParser
from rapidsms.apps.base import AppBase

args = [_("Test name"), {}, _("Test description."), {}]
INFO_EFFECT = lambda: info(*args)
ERROR_EFFECT = lambda: error(*args)
WARN_EFFECT = lambda: warn(*args)
URGENT_EFFECT = lambda: urgent(*args)

CALLED_APPS = {}

class MockApp(OperationBase):

    def classname(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        OperationBase.__init__(self, *args, **kwargs)
        CALLED_APPS[self.classname()] = []

        self.return_values = kwargs.get("return_values")

    def parse_arguments(self, opcode, argstring, message):
        if self.return_values == None:
            return_value = ( [INFO_EFFECT()], { 'equipment_id': 'A' } )
        else:
            return_value = return_values[len(CALLED_APPS[self.classname()])]

        results = {
            'opcode': opcode,
            'argstring': argstring
        }
        CALLED_APPS[self.classname()].append(results)

        return return_value

class MockApp1(MockApp):
    pass

class MockApp2(MockApp):
    pass

class MockSubscriber:

    def __init__(self, signal, app):
        self.return_value = None
        self.side_effects = None

        self.calls = []
        
        self.signal = signal
        self.app = app

    def __enter__(self):
        self.signal.connect(self, sender=self.app, weak=False)
        return self

    def __exit__(self, type, value, tb):
        self.signal.disconnect(self)

    def __call__(self, *args, **kwargs):
        self.calls.append( (args, kwargs) )

        if self.return_value:
            return_value = self.return_value
        else:
            return_value = [INFO_EFFECT()]

        return return_value

class MockRouter(BlockingRouter):

    REGISTERED_OPCODES = []

    @classmethod
    def register_app(cls, opcode, app):
        MockRouter.REGISTERED_OPCODES.append(opcode)
        settings.SIM_OPERATION_CODES[opcode.upper()] = app

    @classmethod
    def unregister_apps(cls):
        MockRouter.REGISTERED_OPCODES = []
        for opcode in MockRouter.REGISTERED_OPCODES:
            del settings.SIM_OPERATION_CODES[opcode]

    def __init__(self, *args, **kwargs):
        registered_apps = [settings.SIM_OPERATION_CODES[opcode] for opcode in MockRouter.REGISTERED_OPCODES]

        kwargs['apps'] = settings.APPS_BEFORE_SIM + (OperationParser,) + tuple(registered_apps) + settings.APPS_AFTER_SIM
        BlockingRouter.__init__(self, *args, **kwargs)
        
class OperationBaseTest(CustomRouterMixin, TestCase):

    router_class = "utils.tests.MockRouter"

    def receive(self, text):
        CustomRouterMixin.receive(self, text, self.lookup_connections('mockbackend', ['4257886710'])[0])

    def tearDown(self):
        MockRouter.unregister_apps()

    def setUp(self):
        global CALLED_APPS
        CALLED_APPS = {}

        MockRouter.register_app("ZZ", MockApp1)
        MockRouter.register_app("QQ", MockApp2)

    def assertParseCalled(self, times, app):
        self.assertEqual(times, len(CALLED_APPS[app]))

    def assertSignalCalled(self, times, subscriber):
        self.assertEqual(times, len(subscriber.calls))

    def test_calls_syntax(self):
        '''Tests that the syntax check is called on a single operation.'''
        self.receive("zz")

        zz, = CALLED_APPS['MockApp1']
        self.assertParseCalled(1, "MockApp1")
        
    def test_calls_semantics(self):
        '''Tests that the semantics check is called on a single operation.'''
        with MockSubscriber(semantic_signal, MockApp1) as sub:
            self.receive("zz")
            
            self.assertSignalCalled(1, sub)

            _, kwargs = sub.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))

    def test_calls_commit(self):
        with MockSubscriber(commit_signal, MockApp1) as sub:
            self.receive("zz")
            
            _, kwargs = sub.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))


    def test_calls_syntax_for_multiple(self):
        self.receive("zzqqzz")

        self.assertParseCalled(2, "MockApp1")
        self.assertParseCalled(1, "MockApp2")

        for args in CALLED_APPS['MockApp1'] + CALLED_APPS['MockApp2']:
            self.assertIn('argstring', args)
            self.assertIn('opcode', args)

    def test_calls_semantics_for_multiple(self):
        with MockSubscriber(semantic_signal, MockApp1) as sub1, \
             MockSubscriber(semantic_signal, MockApp2) as sub2:
            
            self.receive("zzqqzz")

            self.assertSignalCalled(2, sub1)
            self.assertSignalCalled(1, sub2)

            _, kwargs = sub1.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))

            _, kwargs = sub1.calls[1]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))

            _, kwargs = sub2.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))

    def test_calls_commit_for_multiple(self):
        with MockSubscriber(commit_signal, MockApp1) as sub1, \
             MockSubscriber(commit_signal, MockApp2) as sub2:
            
            self.receive("zzqqzz")

            self.assertSignalCalled(2, sub1)
            self.assertSignalCalled(1, sub2)

            _, kwargs = sub1.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))

            _, kwargs = sub1.calls[1]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))

            _, kwargs = sub2.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))