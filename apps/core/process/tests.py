from django.urls import reverse
from rest_framework import status
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


# Create your tests here.


class TestCaseProcess(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()
