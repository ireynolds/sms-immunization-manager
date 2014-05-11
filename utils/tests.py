from django.conf import settings
from django.test import TestCase
from operations import OperationBase, semantic_signal, commit_signal
from operation_parser.app import OperationParser
from django.dispatch.dispatcher import receiver
from rapidsms.contrib.messagelog.app import MessageLogApp
from rapidsms.router.blocking import BlockingRouter
from rapidsms.tests.harness.router import CustomRouterMixin

class LogCalledMixin(TestCase):
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

class MockApp(OperationBase):

    def __init__(self, router):
        OperationBase.__init__(self, router)
        settings.SIM_OPERATION_CODES['zz'] = MockApp

    def get_opcodes(self):
        return ["zz"]

    def parse_arguments(self, **args):
        '''Replaced in send helper method.'''

class MockRouter(BlockingRouter):
    def __init__(self, *args, **kwargs):
        kwargs['apps'] = settings.APPS_BEFORE_SIM + (MockApp,) + settings.APPS_AFTER_SIM
        BlockingRouter.__init__(self, *args, **kwargs)

class Namespace:
    pass

class IntegrationTests(CustomRouterMixin, LogCalledMixin, TestCase):

    router_class = "utils.tests.MockRouter"

    def __init__(self, arg):
        LogCalledMixin.__init__(self, arg)
        CustomRouterMixin.__init__(self)

    ## Helpers

    def send(self, text, parse=None, semantics=None, commit=None):
        AppClass = MockApp

        # Create a namespace to store the returned values
        ns = Namespace()
        ns.semantics_args = None
        ns.commit_args = None
        ns.responses = []

        # Capture args for and add custom handler for parse stage
        @self.log_if_called('syntax', self.called_fns)
        def capture_parse(*args, **kwargs):
            if parse: parse(*args, **kwargs)

        # Store args to semantic stage
        @receiver(semantic_signal, sender=AppClass, weak=False)
        @self.log_if_called('semantics', self.called_fns)
        def capture_semantics(**kwargs): 
            ns.semantics_args = kwargs

        # Add custom semantic subscriber
        if semantics: semantic_signal.connect(semantics, sender=AppClass, weak=False)
        
        # Store args to commit stage
        @receiver(commit_signal, sender=AppClass, weak=False)
        @self.log_if_called('commit', self.called_fns)
        def capture_commit(**kwargs): 
            ns.commit_args = kwargs

        # Add custom commit stage subscriber
        if commit: commit_signal.connect(commit, sender=AppClass, weak=False)

        # Run the message through the router
        self.receive(text, self.lookup_connections('mockbackend', ['4257886710'])[0])

        # Disconnect testing subscribers
        semantic_signal.disconnect(capture_semantics)
        if semantics: semantic_signal.disconnect(semantics)
        commit_signal.disconnect(capture_commit)
        if commit: commit_signal.disconnect(commit)

        return ns

    ## Tests

    def test_simple(self):
        self.send("zz")
        self.assertCalled('syntax', 'semantics', 'commit')