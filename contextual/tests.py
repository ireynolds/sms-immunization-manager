from utils.tests import SIMTestCase
from app import FacilityCode
from utils.tests import MockApp, MockRouter, CustomRouterMixin
from operation_parser.app import OperationParser
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

    def test_delims_before(self):
        message = self.receive("ZZFC  ;, 1")
        fields, effects = message.fields, message.fields['operation_effects']

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertInfoIn(effects)

    def test_delims_after(self):
        message = self.receive("ZZFC 12 ;, ")
        fields, effects = message.fields, message.fields['operation_effects']

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertInfoIn(effects)

    def test_no_id(self):
        message = self.receive("ZZFC ")
        fields, effects = message.fields, message.fields['operation_effects']

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertErrorIn(effects)

    def test_chars_after_id(self):
        message = self.receive("ZZFC 133 1")
        fields, effects = message.fields, message.fields['operation_effects']

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertErrorIn(effects)

    def test_invalid_chars_for_id(self):
        message = self.receive("ZZFC A")
        fields, effects = message.fields, message.fields['operation_effects']

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertErrorIn(effects)

    def test_chars_after_id_nodelims(self):
        message = self.receive("ZZFC 11B")
        fields, effects = message.fields, message.fields['operation_effects']

        self.assertIn('facility', fields)
        self.assertNotEqual(None, fields['facility'])
        self.assertInfoIn(effects)
