from django.urls import reverse
from rest_framework import status

from apps.masterdata.promotion.models import Promotion
from apps.masterdata.saledata.tests import ProductTestCase
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


class PromotionTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

    # for using test create promotion
    def create_uom_group(self):
        url = reverse('UnitOfMeasureGroupList')
        response = self.client.post(
            url,
            {
                'title': 'Time',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def test_create_promotion(self):
        currency_data = {
            "abbreviation": "CAD",
            "title": "CANADIAN DOLLAR",
            "rate": 0.45
        }
        currency = self.client.post(reverse("CurrencyList"), currency_data, format='json')
        product_type = ProductTestCase.create_product_type(self).data['result']  # noqa
        product_category = ProductTestCase.create_product_category(self).data['result']
        unit_of_measure, uom_group = ProductTestCase.create_uom(self)
        data1 = {
            "code": "P01",
            "title": "Laptop HP 6R",
            "product_choice": [],
            'product_type': product_type['id'],
            'product_category': product_category['id'],
            'uom_group': uom_group.data['result']['id']

        }
        product = self.client.post(reverse("ProductList"), data1, format='json')
        data = {
            'title': 'promotion test',
            'currency': currency.data['result']['id'],
            'remark': 'lorem ipsum dolor sit amet.',
            'valid_date_start': '2023-04-15',
            'valid_date_end': '2023-10-20',
            'customer_type': 0,
            'is_discount': True,
            'discount_method': {
                "before_after_tax": True,
                "percent_fix_amount": True,
                "percent_value": 1,
                "use_count": 1,
                "times_condition": 1,
                "is_on_product": True,
                "product_selected": product.data['result']['id']
            },
        }
        url = reverse('PromotionList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_get_list_promotion(self):
        self.test_create_promotion()
        url = reverse('PromotionList')
        response = self.client.get(url, format='json')
        self.assertResponseList( # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

    def test_get_detail_promotion(self):
        res = self.test_create_promotion()
        url = reverse('PromotionDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('title', ''), None, response.status_code)

    def test_update_detail_promotion(self):
        res = self.test_create_promotion()
        url = reverse('PromotionDetail', args=[res.data['result'].get('id', '')])
        get_detail = self.client.get(url, format='json')
        data = get_detail.data['result']
        data['title'] = 'promotion test update'
        data['currency'] = data['currency']['id']
        data['discount_method']['product_selected'] = data['discount_method']['product_selected']['id']
        del [data['customer_remark'], data['customer_by_list'], data['customer_by_condition'], data['is_gift'],
             data['gift_method']]
        self.client.put(url, data, format='json')
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        # self.assertDictEqual(response.data['result'], data)

    def test_delete_detail_promotion(self):
        res = self.test_create_promotion()
        url = reverse('PromotionDetail', args=[res.data['result'].get('id', '')])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Promotion.objects.filter(pk=res.data['result']['id']).exists())
