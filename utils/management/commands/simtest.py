from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os
import sys

class Command(BaseCommand):
    help = 'Runs tests for SIM only'

    def handle(self, *args, **options):
        from django.core.management import execute_from_command_line
        
        command = "./manage.py test " + " ".join(settings.SIM_PRE_APPS + settings.SIM_APPS)
        execute_from_command_line(command.split())