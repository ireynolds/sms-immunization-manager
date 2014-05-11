import mock
from django.test import TestCase
from operations import OperationBase, semantic_signal, commit_signal
from moderation.models import *
from django.utils.translation import ugettext_noop as _
from rapidsms.tests.harness.router import CustomRouterMixin
from rapidsms.router.blocking import BlockingRouter
from operation_parser.app import OperationParser
from rapidsms.apps.base import AppBase
from django.dispatch.dispatcher import _make_id

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

    def parse_arguments(self, opcode, argstring, message):
        if self.return_values == None:
            return_value = ( [INFO_EFFECT()], { 'equipment_id': 'A' } )
        else:
            return_value = self.__class__.return_values[len(CALLED_APPS[self.classname()])]

        results = {
            'opcode': opcode,
            'argstring': argstring
        }
        CALLED_APPS[self.classname()].append(results)

        return return_value

class MockAppZZ(MockApp):
    return_values = None

class MockAppQQ(MockApp):
    return_values = None

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
        self.signal.disconnect(self, self.app)

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
        MockAppZZ.return_values = None
        MockAppQQ.return_values = None

    def setUp(self):
        global CALLED_APPS
        CALLED_APPS = {}

        MockRouter.register_app("ZZ", MockAppZZ)
        MockRouter.register_app("QQ", MockAppQQ)

    def assertParseCalled(self, times, app):
        self.assertEqual(times, len(CALLED_APPS[app.__name__]))

    def assertSignalCalled(self, times, subscriber):
        self.assertEqual(times, len(subscriber.calls))

    def test_connect_and_disconnect(self):
        n_subs = len(commit_signal.receivers)
        self.assertEqual(n_subs, len(commit_signal.receivers))
        with MockSubscriber(commit_signal, MockAppZZ) as sub:
            self.assertEqual(n_subs + 1, len(commit_signal.receivers))
        self.assertEqual(n_subs, len(commit_signal.receivers))

    def test_calls_syntax(self):
        '''Tests that the syntax check is called on a single operation.'''
        self.receive("zz")

        zz, = CALLED_APPS['MockAppZZ']
        self.assertParseCalled(1, MockAppZZ)
        
    def test_calls_semantics(self):
        '''Tests that the semantics check is called on a single operation.'''
        with MockSubscriber(semantic_signal, MockAppZZ) as sub:
            self.receive("zz")
            
            self.assertSignalCalled(1, sub)

            _, kwargs = sub.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))

    def test_calls_commit(self):
        with MockSubscriber(commit_signal, MockAppZZ) as sub:
            self.receive("zz")
            
            self.assertSignalCalled(1, sub)

            _, kwargs = sub.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']), 
                sorted(kwargs.keys()))


    def test_calls_syntax_for_multiple(self):
        self.receive("zzqqzz")

        self.assertParseCalled(2, MockAppZZ)
        self.assertParseCalled(1, MockAppQQ)

        for args in CALLED_APPS['MockAppZZ'] + CALLED_APPS['MockAppQQ']:
            self.assertIn('argstring', args)
            self.assertIn('opcode', args)

    def test_calls_semantics_for_multiple(self):
        with MockSubscriber(semantic_signal, MockAppZZ) as sub1, \
             MockSubscriber(semantic_signal, MockAppQQ) as sub2:
            
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
        with MockSubscriber(commit_signal, MockAppZZ) as sub1, \
             MockSubscriber(commit_signal, MockAppQQ) as sub2:
            
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

    def test_bad_syntax(self):
        with MockSubscriber(semantic_signal, MockAppZZ) as sem_zz, \
             MockSubscriber(semantic_signal, MockAppQQ) as sem_qq, \
             MockSubscriber(commit_signal, MockAppZZ) as com_zz, \
             MockSubscriber(commit_signal, MockAppQQ) as com_qq:

            MockAppQQ.return_values = [([ERROR_EFFECT()], {})]

            self.receive("zzqq12")

            self.assertParseCalled(1, MockAppZZ)
            self.assertSignalCalled(1, sem_zz)
            self.assertSignalCalled(0, com_zz)

            self.assertParseCalled(1, MockAppQQ)
            self.assertSignalCalled(0, sem_qq)
            self.assertSignalCalled(0, com_qq)

    def test_bad_semantics(self):
        with MockSubscriber(semantic_signal, MockAppZZ) as sem_zz, \
             MockSubscriber(semantic_signal, MockAppQQ) as sem_qq, \
             MockSubscriber(commit_signal, MockAppZZ) as com_zz, \
             MockSubscriber(commit_signal, MockAppQQ) as com_qq:

            sem_zz.return_value = [ERROR_EFFECT()]

            self.receive("zzqq a")

            self.assertParseCalled(1, MockAppZZ)
            self.assertSignalCalled(1, sem_zz)
            self.assertSignalCalled(0, com_zz)

            self.assertParseCalled(1, MockAppQQ)
            self.assertSignalCalled(1, sem_qq)
            self.assertSignalCalled(0, com_qq)

    def test_exception_semantic_check_halts(self):
        with MockSubscriber(semantic_signal, MockAppZZ) as sem_zz, \
             MockSubscriber(commit_signal, MockAppZZ) as com_zz:

            sem_zz.return_value = Exception()

            self.receive("zz")

            self.assertParseCalled(1, MockAppZZ)
            self.assertSignalCalled(1, sem_zz)
            self.assertSignalCalled(0, com_zz)
