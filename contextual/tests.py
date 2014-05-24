from utils.tests import SIMTestCase
from app import FacilityCode
from utils.tests import MockApp, MockRouter
from operation_parser.app import OperationParser
from rapidsms.tests.harness.router import CustomRouterMixin
from user_registration.models import Facility

class BlankApp(MockApp):
    return_values = None
    def parse_arguments(*args, **kwargs):
        pass

class FacilityCodeTest(CustomRouterMixin, SIMTestCase):

    router_class = "utils.tests.MockRouter"

    def setUp(self):
        MockRouter.register_app("ZZ", BlankApp)

    def tearDown(self):
        MockRouter.unregister_apps()

    def receive(self, text):
        '''
        Treat the given text as the body of an incoming message and route it through
        the phases of RapidSMS as from number '4257886710' and 'mockbackend'.
        '''
        contact = self.create_contact()
        contact.contactprofile.facility = Facility()

        connection = self.create_connection({'contact': contact})
        message = CustomRouterMixin.receive(self, text, connection)
        return message.fields, message.fields['operation_effects']

    def test_delims_before(self):
        fields, effects = self.receive("ZZFC  ;, 1")

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertInfoIn(effects)

    def test_delims_after(self):
        fields, effects = self.receive("ZZFC 12 ;, ")

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertInfoIn(effects)

    def test_no_id(self):
        fields, effects = self.receive("ZZFC ")

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertErrorIn(effects)

    def test_chars_after_id(self):
        fields, effects = self.receive("ZZFC 133 1")

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertErrorIn(effects)

    def test_invalid_chars_for_id(self):
        fields, effects = self.receive("ZZFC A")

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertErrorIn(effects)

    def test_chars_after_id_nodelims(self):
        fields, effects = self.receive("ZZFC 11B")

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertInfoIn(effects)
