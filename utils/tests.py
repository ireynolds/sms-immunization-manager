from django.conf import settings
from django.test import TestCase

from rapidsms.tests.harness.router import CustomRouterMixin 
CustomRouterMixin.router_class = settings.RAPIDSMS_ROUTER

class CustomRouterTest(CustomRouterMixin, TestCase):
    pass
    # def test_simple(self):
    #     self.receive("so a", self.lookup_connections('mockbackend', ['4257886710'])[0])