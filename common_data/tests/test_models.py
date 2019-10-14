import datetime

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from common_data import models

TODAY = datetime.date.today()

def create_test_common_entities(cls):
    '''Creates common entities for multiple applications
    
    1. individual
    2. organization'''

    cls.individual = models.Individual.objects.create(
        first_name="test",
        last_name="last_name")

    cls.organization = models.Organization.objects.create(
        legal_name="business"
    )

    if models.GlobalConfig.objects.all().count() > 0:
        config = models.GlobalConfig.objects.first()
        config.last_license_check = TODAY
        config.save()

def create_test_user(cls):
    '''creates a test user that can be logged in for view tests'''
    if not hasattr(cls, 'user'):
        cls.user = User.objects.create_superuser('Testuser', 
            'admin@test.com', '123')
        cls.user.save()
