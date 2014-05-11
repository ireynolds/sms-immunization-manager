import mock
from django.test import TestCase
from operations import OperationBase
from moderation.models import *
from django.utils.translation import ugettext_noop as _
from rapidsms.tests.harness.router import CustomRouterMixin
from rapidsms.router.blocking import BlockingRouter
from operation_parser.app import OperationParser
from rapidsms.apps.base import AppBase

args = [_("Test name"), {}, _("Test description."), {}]
INFO_EFFECT = info(*args)
ERROR_EFFECT = error(*args)
WARN_EFFECT = warn(*args)
URGENT_EFFECT = urgent(*args)

class TestApp(OperationBase):

    return_value = None
    side_effects = None
    
    called = None
    called_with_opcode = None
    called_with_argstring = None

    def parse_arguments(self, opcode, argstring, message):
        TestApp.called = True
        TestApp.called_with_opcode = opcode
        TestApp.called_with_argstring = argstring

        if self.side_effects and TestApp.return_value:
            self.side_effects()
        elif self.side_effects:
            return self.side_effects()
        return TestApp.return_value

settings.SIM_OPERATION_CODES['ZZ'] = TestApp

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

    def tearDown(self):
        MockRouter.unregister_apps()

    def test_calls_syntax(self):
        '''Tests that the syntax check is called on a single operation.'''
        MockRouter.register_app(TestApp)
        TestApp.return_value = (
            [INFO_EFFECT], 
            { 'equipment_id': 'a' }
        )

        self.receive("zz a", self.lookup_connections('mockbackend', ['4257886710'])[0])

        self.assertTrue(TestApp.called)
        self.assertEqual("ZZ", TestApp.called_with_opcode)
        self.assertEqual("A", TestApp.called_with_argstring)