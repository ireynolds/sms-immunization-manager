"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings
from rapidsms.tests.harness import RapidTest
from messagelog.app import MessageLogApp
from rapidsms.models import Connection, Contact, Backend
from user_registration.apps import PreferredLanguage
from user_registration.signals import *
from user_registration.models import ContactProfile, get_connection
from utils.tests import *

class PreferredLanguageTest(TestCase):
    """
    All tests involving the PL opcode
    """

    def setUp(self):
        self.pl = PreferredLanguage(None)
        self.OP_CODE = self.pl.get_opcodes().pop()

    def send_args(self, arg_string):
        return self.pl.parse_arguments(self.OP_CODE, arg_string, None)

    def test_simple(self):
        effects, kwargs = self.send_args("1")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['preferred_lang_code'], 1)
        self.assertEqual(kwargs['preferred_lang'], 'English')

    def test_extra_char(self):
        effects, kwargs = self.send_args("1 2")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_unrecognized_char(self):
        effects, kwargs = self.send_args("4")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_unrecognized_chars(self):
        effects, kwargs = self.send_args("456")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

        
        effects, kwargs = self.send_args("abc")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_no_lang_code(self):
        effects, kwargs = self.send_args("")

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

class PreferredLanguageSignalTest(RapidTest):
    def setUp(self):
        self.contact = self.create_contact({'name' : "tester #1"})
        self.connection = self.create_connection({'contact' : self.contact})
        self.data = {
            'text' : "hello world!",
            'connections' : [self.connection]
        }

    def createMessage(self):
        msgLogger = MessageLogApp(None)
        message = self.create_incoming_message(self.data)
        msgLogger.parse(message)

        message.fields = {}
        message.fields['operation_effects'] = []
        return message

    def test_commit_simple(self):
        self.assertEqual(self.contact.language, u'')

        kwargs = {'preferred_lang_code' : 1, 'preferred_lang' : 'English'}
        self.mesg = self.createMessage() 
        effects = preferred_language_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(self.contact.language, "English")
        
        cp = ContactProfile.objects.get(contact=self.contact.pk)
        self.assertEqual(cp.contact.language, "English")

class UserRegistrationTest(TestCase):
    """
    All tests involving the RG opcode
    """

    def setUp(self):
        self.rg = UserRegistration(None)
        self.OP_CODE = self.rg.get_opcodes().pop()

    def send_args(self, arg_string):
        return self.rg.parse_arguments(self.OP_CODE, arg_string, None)
    
    def test_simple_8digit(self):
        effects, kwargs = self.send_args("12345678")

        self.assertEqual(len(effects), 1)
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['phone_number'], '12345678')

    def test_simple_with_dash(self):
        effects, kwargs = self.send_args("1234-5678")

        self.assertEqual(len(effects), 1)
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['phone_number'], '1234-5678')

    def test_simple_13digit(self):
        effects, kwargs = self.send_args("+1234567800000")

        self.assertEqual(len(effects), 1)
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['phone_number'], '+1234567800000')

    def test_simple_phone_and_name(self):
        effects, kwargs = self.send_args("10203040 first_name middle_name last_name")

        self.assertEqual(len(effects), 1)
        self.assertEqual(len(kwargs), 2)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertEqual(kwargs['phone_number'], '10203040')
        self.assertEqual(kwargs['contact_name'], 'first_name middle_name last_name')

    def test_invalid_phone(self):
        effects, kwargs = self.send_args("123 Laura Smith")

        self.assertEqual(len(effects), 1)
        self.assertEqual(kwargs, None)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_no_phone(self):
        effects, kwargs = self.send_args("")

        self.assertEqual(len(effects), 1)
        self.assertEqual(kwargs, None)
        self.assertEqual(effects[0].priority, 'ERROR')

class UserRegistrationSignalTest(RapidTest):
    def setUp(self):
        self.contact = self.create_contact({'name' : "tester #1"})
        self.connection = self.create_connection({'contact' : self.contact})
        self.data = {
            'text' : "hello world!",
            'connections' : [self.connection]
        }
        self.hierarchyNode = HierarchyNode.objects.create(name="Level1")
        self.facility = Facility.objects.create(facility_code=1, name="ABC", hierarchy_node=self.hierarchyNode)

    def createMessage(self):
        msgLogger = MessageLogApp(None)
        message = self.create_incoming_message(self.data)
        msgLogger.parse(message)

        message.fields = {}
        message.fields['operation_effects'] = []
        return message

    def test_commit_simple(self):
        kwargs = {'phone_number' : "12345678"}
        self.mesg = self.createMessage() 

        # Check that no Connection previously exists for this new user
        self.assertIsNone(get_connection(kwargs['phone_number']))
        effects = user_registration_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        
        # Check that Connection and associated Contact and ContactProfile exists
        cxn = get_connection(kwargs['phone_number'])
        self.assertIsNotNone(cxn)
        self.assertEqual(cxn.identity, kwargs['phone_number'])
        cp = ContactProfile.objects.get(contact=cxn.contact.pk)
        self.assertIsNotNone(cp)

    def test_new_backend(self):
        Backend.objects.all().delete()
        self.assertEqual(len(Backend.objects.all()), 0)

        kwargs = {'phone_number' : "1234-1234"}
        self.mesg = self.createMessage()

        self.assertIsNone(get_connection(kwargs['phone_number']))
        effects = user_registration_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        
        cxn = get_connection(kwargs['phone_number'])
        self.assertIsNotNone(cxn)
        self.assertEqual(cxn.identity, kwargs['phone_number'])
        self.assertEqual(cxn.backend.name, settings.PHONE_BACKEND)
        cp = ContactProfile.objects.get(contact=cxn.contact.pk)
        self.assertIsNotNone(cp)

    def test_contact_already_exists(self):
        kwargs = {'phone_number' : "12345678"}
        self.mesg = self.createMessage()
        self.assertIsNotNone(self.mesg.connections[0])

        effects = user_registration_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')
        self.assertIsNotNone(self.mesg.connections[0].contact)

        # try to add same user again
        effects = user_registration_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')

    def test_contact_name(self):
        kwargs = {'phone_number' : "12341111",
                  'contact_name' : "Alice Walker"}
        self.mesg = self.createMessage()
        self.assertIsNotNone(self.mesg.connections[0])

        effects = user_registration_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')

        cxn = get_connection(kwargs['phone_number'])
        self.assertIsNotNone(cxn)
        self.assertEqual(cxn.identity, kwargs['phone_number'])
        self.assertEqual(cxn.backend.name, settings.PHONE_BACKEND)
        self.assertEqual(cxn.contact.name, "Alice Walker")
        cp = ContactProfile.objects.get(contact=cxn.contact.pk)
        self.assertIsNotNone(cp)


    def test_facility_code(self):
        kwargs = {"phone_number" : "11110000"}
        self.mesg = self.createMessage()
        self.mesg.connections[0].contact.contactprofile.facility = self.facility
        
        temp_facility = Facility.objects.create(facility_code=2, name="XYZ", hierarchy_node=self.hierarchyNode)
        self.mesg.fields['facility'] = temp_facility

        self.assertIsNotNone(self.mesg.connections[0])

        effects = user_registration_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')

        cxn = get_connection(kwargs['phone_number'])
        self.assertIsNotNone(cxn)
        self.assertEqual(cxn.identity, kwargs['phone_number'])
        self.assertEqual(cxn.backend.name, settings.PHONE_BACKEND)
        cp = ContactProfile.objects.get(contact=cxn.contact.pk)
        self.assertIsNotNone(cp)
        self.assertEqual(cp.facility, temp_facility)
        

    def test_no_facility_code(self):
        kwargs = {"phone_number" : "+1234567812345"}
        self.mesg = self.createMessage()
        self.assertIsNotNone(self.mesg.connections[0])
        self.mesg.connections[0].contact.contactprofile.facility = self.facility
        self.assertEqual(len(self.mesg.fields), 1)

        effects = user_registration_commit(self.mesg, **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')

        cxn = get_connection(kwargs['phone_number'])
        self.assertIsNotNone(cxn)
        self.assertEqual(cxn.identity, kwargs['phone_number'])
        self.assertEqual(cxn.backend.name, settings.PHONE_BACKEND)
        cp = ContactProfile.objects.get(contact=cxn.contact.pk)
        self.assertIsNotNone(cp)
        self.assertEqual(cp.facility, self.facility)



