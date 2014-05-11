import mock
from django.test import TestCase
from operations import OperationBase, semantic_signal
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

class TestApp(OperationBase):

    return_effects = None
    return_kwargs = None

    called = None
    called_with_opcode = None
    called_with_argstring = None

    def parse_arguments(self, opcode, argstring, message):
        TestApp.called = True
        TestApp.called_with_opcode = opcode
        TestApp.called_with_argstring = argstring

        return_value = (
            TestApp.return_effects if TestApp.return_effects else [INFO_EFFECT()],
            TestApp.return_kwargs if TestApp.return_kwargs else { 'equipment_id': 'A' }
        )

        return return_value

settings.SIM_OPERATION_CODES['ZZ'] = TestApp

class MockSemanticsSubscriber:

    return_value = None
    side_effects = None

    called = None
    called_with_args = None
    called_with_kwargs = None

    def __enter__(self):
        semantic_signal.connect(self, sender=TestApp, weak=False)
        return self

    def __exit__(self, type, value, tb):
        semantic_signal.disconnect(self)

    def __call__(self, *args, **kwargs):
        MockSemanticsSubscriber.called = True
        MockSemanticsSubscriber.called_with_args = args
        MockSemanticsSubscriber.called_with_kwargs = kwargs

        if MockSemanticsSubscriber.return_value:
            return_value = MockSemanticsSubscriber.return_value
        else:
            return_value = [INFO_EFFECT()]

        return return_value

class MockRouter(BlockingRouter):
    REGISTERED_APPS = []

    @classmethod
    def register_app(cls, appname):
        MockRouter.REGISTERED_APPS.append(appname)

    @classmethod
    def unregister_apps(cls):
        MockRouter.REGISTERED_APPS = []

    def __init__(self, *args, **kwargs):
        kwargs['apps'] = settings.APPS_BEFORE_SIM + (OperationParser,) + tuple(MockRouter.REGISTERED_APPS) + settings.APPS_AFTER_SIM
        BlockingRouter.__init__(self, *args, **kwargs)
        
class OperationBaseTest(CustomRouterMixin, TestCase):
    router_class = "utils.tests.MockRouter"

    def receive(self, text):
        CustomRouterMixin.receive(self, text, self.lookup_connections('mockbackend', ['4257886710'])[0])

    def tearDown(self):
        MockRouter.unregister_apps()

    def setUp(self):
        MockRouter.register_app(TestApp)

    def test_calls_syntax(self):
        '''Tests that the syntax check is called on a single operation.'''
        self.receive("zz a")

        self.assertTrue(TestApp.called)
        self.assertEqual("ZZ", TestApp.called_with_opcode)
        self.assertEqual("A", TestApp.called_with_argstring)

    def test_calls_semantics(self):
        '''Tests that the semantics check is called on a single operation.'''
        with MockSemanticsSubscriber() as sub:
            self.receive("zz a")

            self.assertTrue(MockSemanticsSubscriber.called)
            kwargs = MockSemanticsSubscriber.called_with_kwargs
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))
            self.assertEqual('A', kwargs['equipment_id'])
            self.assertEqual('ZZ', kwargs['opcode'])
