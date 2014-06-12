"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from django.test import TestCase
from rapidsms.tests.harness import RapidTest
from user_registration.models import ContactProfile, Facility
from messagelog.app import MessageLogApp
from permissions.signals import *

class PermissionsSignalTest(RapidTest):
    def createContact(self, name, role_name):
        self.contact = self.create_contact({'name' : name})
        self.contact.contactprofile.role_name = role_name
        self.contact.contactprofile.save()
        self.connection = self.create_connection({'contact' : self.contact})

    def setUp(self):
        self.createContact("test1", settings.DATA_REPORTER_ROLE)
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

    def test_DataWorker_RG(self):
        self.assertEqual(self.contact.language, u'')

        kwargs = {'preferred_lang_code' : 1, 'preferred_lang' : 'English'}
        self.mesg = self.createMessage() 
        effects = opcode_permissions_check(self.mesg, "RG", **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'ERROR')
        self.assertEqual(self.contact.language, u'')
        
        cp = ContactProfile.objects.get(contact=self.contact.pk)
        self.assertEqual(cp.contact.language, u'')

    def test_Admin_RG(self):
        self.createContact("admin1", settings.ADMIN_ROLE)
        self.data['connections'] = [self.connection]
        self.assertEqual(self.contact.contactprofile.role_name, settings.ADMIN_ROLE)
        self.assertEqual(self.contact.language, u'')

        kwargs = {'preferred_lang_code' : 1, 'preferred_lang' : 'English'}
        self.mesg = self.createMessage() 
        self.assertEqual(self.contact, self.mesg.connections[0].contact)
        effects = opcode_permissions_check(self.mesg, "RG", **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')

    def test_DataWorker_HE(self):
        self.mesg = self.createMessage()
        kwargs = {}
        effects = opcode_permissions_check(self.mesg, "HE", **kwargs)

        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].priority, 'INFO')

    def test_not_allowed_for_facility(self):
        self.mesg = self.createMessage()
        self.mesg.fields['facility'] = Facility(name="test_facility1")
        self.assertNotEqual(self.mesg.fields['facility'],
                            self.contact.contactprofile.facility)

        kwargs = {}
        kwargs['stock_levels'] = { 'P' : 100}
        effects = opcode_permissions_check(self.mesg, "SL", **kwargs)
        self.assertEqual(effects[0].priority, 'ERROR')
 
    def test_allowed_for_facility(self):
        self.mesg = self.createMessage()
        self.mesg.fields['facility'] = Facility(name="test_facility1")
        self.contact.contactprofile.facility = Facility(name="test_facility1")
        self.assertEqual(self.mesg.fields['facility'],
                            self.contact.contactprofile.facility)

        kwargs = {}
        kwargs['stock_levels'] = { 'P' : 100}
        effects = opcode_permissions_check(self.mesg, "SL", **kwargs)
        self.assertEqual(effects[0].priority, 'INFO')
        
 
