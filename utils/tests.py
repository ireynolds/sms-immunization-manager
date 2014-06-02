from django.test import TestCase
from operations import OperationBase, semantic_signal, commit_signal
from moderation.models import *
from django.utils.translation import ugettext_noop as _
from rapidsms.tests.harness.router import CustomRouterMixin as _CustomRouterMixin
from rapidsms.router.blocking import BlockingRouter
from rapidsms.apps.base import AppBase
from django.dispatch.dispatcher import _make_id
from user_registration.models import Facility

###
### Utilities for testing code
###

class SIMTestCase(TestCase):
    '''
    Defines assert* methods useful for testing SIM code.
    '''

    def assertErrorIn(self, effects):
        '''
        Asserts that effects contains at least on MessageEffect with
        priority ERROR.
        '''
        self.assertPriorityIn(ERROR, effects)

    def assertInfoIn(self, effects):
        '''
        Asserts that effects contains at least on MessageEffect with
        priority INFO.
        '''
        self.assertPriorityIn(INFO, effects)

    def assertUrgentIn(self, effects):
        '''
        Asserts that effects contains at least on MessageEffect with
        priority URGENT.
        '''
        self.assertPriorityIn(URGENT, effects)

    def assertPriorityIn(self, priority, effects):
        '''
        Asserts that effects contains at least on MessageEffect with
        the given priority.
        '''
        for effect in effects:
            if effect.priority == priority:
                return
        return self.fail("No %s in %s" % (priority, repr(effects),))

###
### Tests for Utils code
###

args = [_("Test name"), {}, _("Test description."), {}]
INFO_EFFECT = lambda: info(*args)
ERROR_EFFECT = lambda: error(*args)
WARN_EFFECT = lambda: warn(*args)
URGENT_EFFECT = lambda: urgent(*args)

CALLED_APPS = None

class MockApp(OperationBase):
    '''
    Defines a useful mock version of an SMS app that is used to
    test OperationBase by controlling methods' return return values
    and storing the arguments to method calls.
    '''

    # Assigned in subclasses to determine what parse_arguments should
    # return.
    return_values = None

    def _classname(self):
        '''Returns the common name of this. Usually the name of a subtype.'''
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        OperationBase.__init__(self, *args, **kwargs)
        CALLED_APPS[self._classname()] = []

    def parse_arguments(self, opcode, argstring, message):
        '''
        Mocks OperationBase.parse_arguments.

        On the Nth call to parse_arguments, returns the Nth element in the
        self.__class__.return_values list, else some reasonable (INFO) default
        and appends the arguments to the list at CALLED_APPS[${self.__class__.__name__}]
        '''
        if self.return_values == None:
            return_value = ( [INFO_EFFECT()], { 'equipment_id': 'A' } )
        else:
            return_value = self.__class__.return_values[len(CALLED_APPS[self._classname()])]

        arguments = {
            'opcode': opcode,
            'argstring': argstring
        }
        CALLED_APPS[self._classname()].append(arguments)

        return return_value

class MockAppZZ(MockApp):
    '''
    By convention, configured in OperationBaseTest to
    parse "ZZ" opcode.
    '''

    # May be assigned in testing code to determine what
    # values are returned when this class's parse_arguments
    # is called.
    return_values = None

class MockAppQQ(MockApp):
    '''
    By convention, configured in OperationBaseTest to
    parse "QQ" opcode.
    '''

    # May be assigned in testing code to determine what
    # values are returned when this class's parse_arguments
    # is called.
    return_values = None

class MockAppXX(MockApp):
    '''
    By convention, configured in OperationBaseTest to 
    parse "XX" opcode.
    '''

    # May be assigned in testing code to determine what 
    # values are returned when this class's parse_arguments
    # is called.
    return_values = None


class MockSubscriber:
    '''
    Defines a mock version of a module that subscribes to
    semantics and commit signals for a particular app (sender).

    Must be used as "with MockSubscriber(signal, sender) as subscriber" to
    automatically connect to and disconnect from signals for a
    testing period.
    '''

    def __init__(self, signal, app):
        '''
        Stores signal and app as fields of self, but does not connect
        to the signal--use this class in a with statement to
        connect and disconnect.
        '''
        self.return_value = None
        self.side_effects = None

        self.calls = []

        self.signal = signal
        self.app = app

    def __enter__(self):
        '''Connect to self.signal.'''
        self.signal.connect(self, sender=self.app, weak=False)
        return self

    def __exit__(self, type, value, tb):
        '''Disconnect from self.signal.'''
        self.signal.disconnect(self, self.app)

    def __call__(self, *args, **kwargs):
        '''
        Method called when the signal is passed. Returns self.return_value, or
        some reasonable (INFO) default.
        '''
        self.calls.append( (args, kwargs) )

        if self.return_value:
            return_value = self.return_value
        else:
            return_value = [INFO_EFFECT()]

        return return_value

class MockRouter(BlockingRouter):
    '''
    Defines a mock version of a Router that calls all non-SIM apps in
    settings.REGISTERED_APPS, OperationParser, and any app added
    by calling MockRouter.register_app.

    Allows a client to customize what apps are called to isolate
    the OperationParser during testing.
    '''

    REGISTERED_OPCODES = []

    @classmethod
    def register_app(cls, opcode, app, group=settings.PERIODIC, limit_one=False):
        '''
        Register the given app with every instance of MockRouter as handling the
        given opcode.
        '''
        MockRouter.REGISTERED_OPCODES.append(opcode)

        # add given opcode to list of permitted opcodes for all user roles
        role_opcodes = dict(settings.ROLE_OP_CODES)
        for opcodes in role_opcodes.itervalues():
            opcodes.append(opcode)

        settings.SIM_OPERATION_CODES[opcode.upper()] = app
        settings.SIM_OPCODE_GROUPS[opcode.upper()] = group
        if limit_one: settings.SIM_OPCODE_MAY_NOT_DUPLICATE.add(opcode.upper())


    @classmethod
    def unregister_apps(cls):
        '''
        Unregister all apps (that were registered using MockRouter.register_app) from
        every instance of MockRouter.
        '''
        role_opcodes = dict(settings.ROLE_OP_CODES)
        for opcode in MockRouter.REGISTERED_OPCODES:
            for opcodes in role_opcodes.values():
                if opcode in opcodes:
                    opcodes.remove(opcode)
            del settings.SIM_OPERATION_CODES[opcode]
            del settings.SIM_OPCODE_GROUPS[opcode]
            if opcode in settings.SIM_OPCODE_MAY_NOT_DUPLICATE:
                settings.SIM_OPCODE_MAY_NOT_DUPLICATE.remove(opcode)
        MockRouter.REGISTERED_OPCODES = []

    def __init__(self, *args, **kwargs):
        registered_apps = [settings.SIM_OPERATION_CODES[opcode] for opcode in MockRouter.REGISTERED_OPCODES]

        kwargs['apps'] = settings.APPS_BEFORE_SIM + settings.SIM_PRE_APPS + tuple(registered_apps) + settings.APPS_AFTER_SIM
        BlockingRouter.__init__(self, *args, **kwargs)

class CustomRouterMixin(_CustomRouterMixin):
    def receive(self, text):
        '''
        Treat the given text as the body of an incoming message and route it through
        the phases of RapidSMS as from number '4257886710' and 'mockbackend'.
        '''
        contact = self.create_contact()
        contact.contactprofile.facility = Facility()

        connection = self.create_connection({'contact': contact})
        return _CustomRouterMixin.receive(self, text, connection)

class OperationBaseTest(CustomRouterMixin, TestCase):
    '''Tests for OperationBase.'''

    # An instance of this class is used as the router for all calls to
    # self.receive.
    router_class = "utils.tests.MockRouter"

    def setUp(self):
        '''
        Reset mock apps' return values, unregister all apps registered
        with the mock router.
        '''
        global CALLED_APPS
        CALLED_APPS = {}

        MockRouter.register_app("ZZ", MockAppZZ)
        MockRouter.register_app("QQ", MockAppQQ)
        MockRouter.register_app("XX", MockAppXX, limit_one=True)

    def tearDown(self):
        global CALLED_APPS
        CALLED_APPS = {}

        MockAppZZ.return_values = None
        MockAppQQ.return_values = None

        MockRouter.unregister_apps()

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
        self.receive("zz")

        zz, = CALLED_APPS['MockAppZZ']
        self.assertParseCalled(1, MockAppZZ)

    def test_calls_semantics(self):
        with MockSubscriber(semantic_signal, MockAppZZ) as sem:
            self.receive("zz")

            self.assertSignalCalled(1, sem)

            _, kwargs = sem.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']),
                sorted(kwargs.keys()))

    def test_calls_commit(self):
        with MockSubscriber(commit_signal, MockAppZZ) as com:
            self.receive("zz")

            self.assertSignalCalled(1, com)

            _, kwargs = com.calls[0]
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
        with MockSubscriber(semantic_signal, MockAppZZ) as sem_zz, \
             MockSubscriber(semantic_signal, MockAppQQ) as sem_qq:

            self.receive("zzqqzz")

            self.assertSignalCalled(2, sem_zz)
            self.assertSignalCalled(1, sem_qq)

            _, kwargs = sem_zz.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']),
                sorted(kwargs.keys()))

            _, kwargs = sem_zz.calls[1]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']),
                sorted(kwargs.keys()))

            _, kwargs = sem_qq.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']),
                sorted(kwargs.keys()))

    def test_calls_commit_for_multiple(self):
        with MockSubscriber(commit_signal, MockAppZZ) as com_zz, \
             MockSubscriber(commit_signal, MockAppQQ) as com_qq:

            self.receive("zzqqzz")

            self.assertSignalCalled(2, com_zz)
            self.assertSignalCalled(1, com_qq)

            _, kwargs = com_zz.calls[0]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']),
                sorted(kwargs.keys()))

            _, kwargs = com_zz.calls[1]
            self.assertEqual(
                sorted(['message', 'opcode', 'sender', 'signal', 'equipment_id']),
                sorted(kwargs.keys()))

            _, kwargs = com_qq.calls[0]
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

    def test_no_commit_if_parser_errors(self):
        with MockSubscriber(commit_signal, MockAppXX) as com_xx:

            self.receive("xx xx")

            self.assertSignalCalled(0, com_xx)
