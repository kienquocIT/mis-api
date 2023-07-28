from django.urls import reverse
from rest_framework.test import APIClient

from apps.sales.delivery.models import DeliveryConfig
from apps.sales.saleorder.tests import TestCaseSaleOrder
from apps.shared import AdvanceTestCase


class PickingDeliveryTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

        company_data = {
            'title': 'Cty TNHH one member',
            'code': 'MMT',
            'representative_fullname': 'Mike Nguyen',
            'address': '7826 avenue, Victoria Street, California, American',
            'email': 'mike.nguyen.7826@gmail.com',
            'phone': '0983875345',
        }
        company_req = self.client.post(reverse("AccountTypeList"), company_data, format='json')

        config_data = {
            'company': company_req.data['result']['id'],
            'is_picking': False,
            'is_partial_ship': False,
        }
        config = DeliveryConfig.objects.create(
            company_id=company_req.data['result']['id'],
            is_picking=False,
            is_partial_ship=False
        )
        self.config = config.data['result']

        sale_order = TestCaseSaleOrder.test_create_sale_order()

        self.sale_order_id = sale_order.data['result']['id']

    def test_create_picking_and_delivery_from_order(self):
        url = reverse('SaleOrderActiveDelivery', args=[self.sale_order_id])
        create = self.client.post(url, {}, format='json')
        self.assertEqual(create.status_code, 201)
