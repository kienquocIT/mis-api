from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.masterdata.saledata.tests import IndustryTestCase, ConfigPaymentTermTestCase, ProductTestCase, \
    WareHouseTestCase
from apps.sales.delivery.models import DeliveryConfig, OrderDelivery, OrderDeliverySub, OrderDeliveryProduct
from apps.sales.saleorder.models import SaleOrderProduct
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
        company_req = self.client.post(reverse("CompanyList"), company_data, format='json')
        config = DeliveryConfig.objects.get_or_create(
            company_id=company_req.data['result']['id'],
            defaults={
                'is_picking': False,
                'is_partial_ship': False,
            },
        )
        self.config = config[0]

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def get_account_type(self):
        url = reverse("AccountTypeList")
        response = self.client.get(url, format='json')
        return response

    def create_industry(self):
        response = IndustryTestCase.test_create_new(self)
        return response

    def test_create_config_payment_term(self):
        response = ConfigPaymentTermTestCase.test_create_config_payment_term(self)
        self.assertEqual(response.status_code, 201)
        return response

    def get_price_list(self):
        url = reverse('PriceList')
        response = self.client.get(url, format='json')
        return response

    def create_new_tax(self):
        url_tax = reverse("TaxList")
        tax_category = self.create_new_tax_category()
        data = {
            "title": "Thuế bán hành VAT-10%",
            "code": "VAT-10",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response = self.client.post(url_tax, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'title', 'code', 'rate', 'category', 'type'],
            check_sum_second=True,
        )
        return response

    def get_base_unit_measure(self):
        url = reverse('BaseItemUnitList')
        response = self.client.get(url, format='json')
        return response

    def get_currency(self):
        url = reverse('CurrencyList')
        response = self.client.get(url, format='json')
        return response

    def create_product_type(self):
        url = reverse('ProductTypeList')
        response = self.client.post(
            url,
            {
                'title': 'San pham 1',
                'description': '',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def create_product_category(self):
        url = reverse('ProductCategoryList')
        response = self.client.post(
            url,
            {
                'title': 'Hardware',
                'description': '',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

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

    def create_uom(self):
        data_uom_gr = self.create_uom_group()
        url = reverse('UnitOfMeasureList')
        response = self.client.post(
            url,
            {
                "code": "MIN",
                "title": "minute",
                "group": data_uom_gr.data['result']['id'],
                "ratio": 1,
                "rounding": 5,
                "is_referenced_unit": True
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response, data_uom_gr

    def create_new_tax_category(self):
        url_tax_category = reverse("TaxCategoryList")
        data = {
            "title": "Thuế doanh nghiệp kinh doanh tư nhân",
            "description": "Áp dụng cho các hộ gia đình kinh doanh tư nhân",
        }
        response = self.client.post(url_tax_category, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'title', 'description', 'is_default'],
            check_sum_second=True,
        )
        return response

    def test_create_sale_order(self):
        data_salutation = {  # noqa
            "code": "S01ORDER",
            "title": "MrORDER",
            "description": "A man"
        }
        url_salutation = reverse('SalutationList')
        response_salutation = self.client.post(url_salutation, data_salutation, format='json')
        url_contact = reverse("ContactList")
        salutation = response_salutation.data['result']['id']
        employee = self.get_employee().data['result'][0]['id']
        data_contact = {
            "owner": employee,
            "job_title": "Giám đốc nè",
            "biography": "không có",
            "fullname": "Trịnh Tuấn Nam",
            "salutation": salutation,
            "phone": "string",
            "mobile": "string",
            "email": "string",
            "report_to": None,
            "address_information": {},
            "additional_information": {},
            "account_name": None,
            "system_status": 0
        }
        response_contact = self.client.post(url_contact, data_contact, format='json')
        url_account_group = reverse("AccountGroupList")
        data_account_group = {  # noqa
            "code": "AG01ORDER",
            "title": "Nhóm khách hàng test đơn hàng",
            "description": ""
        }
        response_account_group = self.client.post(url_account_group, data_account_group, format='json')
        account_type = self.get_account_type().data['result'][0]['id']
        account_group = response_account_group.data['result']['id']
        contact = response_contact.data['result']['id']
        industry = self.create_industry().data['result']['id']
        data_account = {
            "name": "Công ty hạt giống, phân bón Trúc Phượng",
            "code": "AC01ORDER",
            "website": "trucphuong.com.vn",
            "account_type": [account_type],
            "owner": contact,
            "manager": {employee},
            "parent_account": None,
            "account_group": account_group,
            "tax_code": "string",
            "industry": industry,
            "annual_revenue": 1,
            "total_employees": 1,
            "phone": "string",
            "email": "string",
            "shipping_address": {},
            "billing_address": {},
            "contact_select_list": [
                contact
            ],
            "contact_primary": contact,
            "account_type_selection": 0,
            "system_status": 0
        }
        url = reverse("AccountList")
        response_account = self.client.post(url, data_account, format='json')
        opportunity = None
        customer = response_account.data['result']['id']
        employee = self.get_employee().data['result'][0]['id']
        payment_term = self.test_create_config_payment_term().data['result']['id']
        data = {
            "title": "Đơn hàng test",
            "opportunity": opportunity,
            "customer": customer,
            "contact": contact,
            "sale_person": employee,
            "payment_term": payment_term,
        }
        url = reverse("SaleOrderList")
        response = self.client.post(url, data, format='json')

        self.assertResponseList(
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            [
                'id',
                'title',
                'code',
                'opportunity',
                'customer',
                'contact',
                'sale_person',
                'payment_term',
                'quotation',
                'system_status',
                # sale order tabs
                'sale_order_products_data',
                'sale_order_logistic_data',
                'sale_order_costs_data',
                'sale_order_expenses_data',
                # total amount of products
                'total_product_pretax_amount',
                'total_product_discount_rate',
                'total_product_discount',
                'total_product_tax',
                'total_product',
                'total_product_revenue_before_tax',
                # total amount of costs
                'total_cost_pretax_amount',
                'total_cost_tax',
                'total_cost',
                # total amount of expenses
                'total_expense_pretax_amount',
                'total_expense_tax',
                'total_expense',
                'date_created',
                'delivery_call',
                # indicator tab
                'sale_order_indicators_data',
            ],
            check_sum_second=True,
        )
        self.url = reverse("ProductList")
        prod = ProductTestCase.test_create_product(self)
        prod_detail = prod.data['result']
        warehouse = WareHouseTestCase.test_warehouse_create(self)
        good_receipt_url = reverse("GoodReceiptList")
        good_receipt_data = {
            'title': 'create good receipt',
            'posting_date': '2023-08-20',
            'product_list': [
                {
                    'product': prod_detail['id'],
                    'warehouse': warehouse.data['result']['id'],
                    'uom': prod_detail['uom'],
                    'quantity': 1,
                    'unit_price': 10000,
                    'tax': 0,
                    'subtotal_price': 10000,
                    'order': 1
                }
            ],
            'pretax_amount': 200000,
            'taxes': 0,
            'total_amount': 200000
        }
        stock = self.client.post(good_receipt_url, good_receipt_data, format='json')
        self.assertEqual(stock.status_code, 201)

        SaleOrderProduct.objects.create(
            sale_order_id=response.data['result']['id'],
            product_id=prod_detail['id'],
            product_quantity=1,
            product_unit_price=10000,
            product_discount_value=0,
            product_discount_amount=0,
            product_tax_value=0,
            product_tax_amount=0,
            product_subtotal_price=10000,
            product_subtotal_price_after_tax=10000
        )
        self.assertFalse(SaleOrderProduct.objects.filter(pk=prod_detail['id']).exists())
        return response

    def test_create_picking_and_delivery_from_order(self):
        sale_order_id = self.test_create_sale_order().data['result']['id']
        delivery_url = reverse('SaleOrderActiveDelivery', args=[sale_order_id])
        response = self.client.post(delivery_url, {}, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_complete_delivery(self):
        sale_order_id = self.test_create_sale_order().data['result']['id']
        delivery = OrderDelivery.objects.get(sale_order_id=sale_order_id)
        delivery_sub = OrderDeliverySub.objects.get(order_delivery_id=delivery.id)
        delivery_prod = OrderDeliveryProduct.objects.filter(delivery_sub=delivery_sub).first()
        url_update = reverse('OrderDeliverySubDetail', args=[delivery_sub.id])
        data_delivery_update = {
            "order_delivery": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "estimated_delivery_date": "2023-07-31",
            "actual_delivery_date": "2023-08-30",
            "products": {
                'product_id': delivery_prod.id,
                'done': 1,
                'delivery_data': {
                    'warehouse': delivery_prod.warehouse.id,
                    'uom': delivery_prod.uom.id,
                    'stock': 1
                },
                'order': 1,
            }
        }
        response = self.client.put(url_update, data_delivery_update, format='json')
        self.assertEqual(response.status_code, 201)
        return response
