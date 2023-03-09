from django.test import TestCase
from apps.sale.saledata.models.accounts import *
from rest_framework.exceptions import ValidationError
from apps.sale.saledata.serializers.accounts import *
# Create your tests here.


class AccountTestCase(TestCase):
    def test_duplicate_code(self):
        data_first = {
            'code': 'I001',
            'name': 'Banking',
        }

        data_second = {
            'code': 'I002',
            'name': 'IT Service',
        }

        serializer_first = InterestsCreateSerializer(data=data_first)
        serializer_first.is_valid(raise_exception=True)
        serializer_first.save()
        serializer_second = InterestsCreateSerializer(data=data_second)
        serializer_second.is_valid(raise_exception=True)
        serializer_second.save()

        if serializer_second.errors:
            with self.assertRaises(ValidationError) as context:
                serializer_second.is_valid(raise_exception=True)
            self.assertEqual(set(context.exception.detail.keys()), set(['code']))
            self.assertEqual(context.exception.detail['code'][0], 'Code already exists in database')
