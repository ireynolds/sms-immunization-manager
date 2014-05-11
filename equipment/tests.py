"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from apps import EquipmentRepaired, EquipmentFailure
import operation_parser.app
from utils.operations import commit_signal, semantic_signal

class EquipmentFailureTest(APITest):
    
    sender = EquipmentFailure

    def test_handle_simple(self):
        ns = self.send("NF A")
        self.assertCalled('check', 'commit', 'respond')

        # It is assumed in all other tests that check_args and commit_args have 
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('equipment_id', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('equipment_id', ns.commit_args)

        self.assertEqual(1, len(ns.responses))

    def test_handle_one_valid_arg(self):
        ns = self.send("NF A")
        
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual("A", ns.commit_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_no_arg(self):
        ns = self.send("NF")
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual(None, ns.check_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_two_valid_args(self):
        ns = self.send("NF A B")
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])
    
    def test_one_invalid_arg(self):
        ns = self.send('NF Q')
        self.assertNotCalled('commit')
        self.assertCalled('check', 'respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])

    def test_valid_followed_by_junk(self):
        ns = self.send('NF A001')
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])

class EquipmentRepairedTest(APITest):

    sender = EquipmentRepaired

    def test_handle_simple(self):
        ns = self.send("WO A")
        self.assertCalled('check', 'commit', 'respond')

        # It is assumed in all other tests that check_args and commit_args have 
        # the same keys and (mostly) the same values.

        self.assertIn('message', ns.check_args)
        self.assertIn('equipment_id', ns.check_args)

        self.assertIn('message', ns.commit_args)
        self.assertIn('equipment_id', ns.commit_args)

        self.assertEqual(1, len(ns.responses))

    def test_handle_one_valid_arg(self):
        ns = self.send("WO A")
        
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual("A", ns.commit_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_no_arg(self):
        ns = self.send("WO")
        self.assertCalled('check', 'commit', 'respond')

        self.assertEqual(None, ns.check_args['equipment_id'])

        self.assertEqual(1, len(ns.responses))        
        self.assertIn('Success', ns.responses[0])

    def test_with_two_valid_args(self):
        ns = self.send("WO A B")
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])
    
    def test_one_invalid_arg(self):
        ns = self.send('WO Q')
        self.assertNotCalled('commit')
        self.assertCalled('check', 'respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])

    def test_valid_followed_by_junk(self):
        ns = self.send('WO A001')
        self.assertNotCalled('check', 'commit')
        self.assertCalled('respond')

        self.assertEqual(1, len(ns.responses))
        self.assertIn("OK until", ns.responses[0])