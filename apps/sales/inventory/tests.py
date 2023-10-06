from urllib.parse import urlencode
from uuid import uuid4

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.masterdata.saledata.tests import WareHouseTestCase, ProductTestCase, IndustryTestCase, \
    ConfigPaymentTermTestCase
from apps.sales.delivery.models import DeliveryConfig, OrderPickingProduct, OrderPickingSub, OrderPicking, \
    OrderDeliveryProduct, OrderDeliverySub, OrderDelivery
from apps.sales.delivery.tests import PickingDeliveryTestCase
from apps.sales.saleorder.models import SaleOrderProduct
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


# Create your tests here.


class InventoryTestCase(AdvanceTestCase):
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

    def test_1_create_config_payment_term(self):
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
            "tax_type": 0
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
            ['id', 'title', 'code', 'rate', 'category', 'tax_type'],
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

    def get_city(self):
        url = reverse("CityList")
        response = self.client.get(url, format='json')
        return response

    def get_district(self, city_id):
        params = {
            'city_id': city_id
        }
        url = reverse("DistrictList")
        query_string = urlencode(params)
        url_with_query_string = f"{url}?{query_string}"
        response = self.client.get(url_with_query_string, format='json')
        return response

    def get_ward(self):
        url = reverse("WardList")
        response = self.client.get(url, format='json')
        return response

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

    def create_sale_order(self):
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
            "parent_account_mapped": None,
            "account_group": account_group,
            "tax_code": "string",
            "industry": industry,
            "annual_revenue": 1,
            "total_employees": 1,
            "phone": "string",
            "email": "string",
            "account_type_selection": 0,
            "system_status": 0
        }
        url = reverse("AccountList")
        response_account = self.client.post(url, data_account, format='json')
        opportunity = None
        customer = response_account.data['result']['id']
        employee = self.get_employee().data['result'][0]['id']
        payment_term = self.test_1_create_config_payment_term().data['result']['id']
        data = {
            "title": "Đơn hàng test",
            "opportunity": opportunity,
            "customer": customer,
            "contact": contact,
            "employee_inherit_id": employee,
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
                'customer_shipping_id',
                'customer_billing_id',
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
                # system
                'workflow_runtime_id',
                'is_active',
            ],
            check_sum_second=True,
        )
        self.sale_order = response
        self.url = reverse("ProductList")
        prod = ProductTestCase.test_create_product(self)
        prod_detail = prod.data['result']
        warehouse = WareHouseTestCase.test_warehouse_create(self)
        self.warehouse = warehouse
        good_receipt_url = reverse("GoodReceiptList")
        good_receipt_data = {
            'title': 'create good receipt',
            'posting_date': '2023-08-20',
            'product_list': [
                {
                    'product': prod_detail['id'],
                    'warehouse': warehouse.data['result']['id'],
                    'uom': prod_detail['inventory_information']['uom']['uom_id'],
                    'quantity': 100,
                    'unit_price': 10000,
                    'tax': prod_detail['sale_information']['tax']['id'],
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

    def update_config_picking(self):
        url_config = reverse('DeliveryConfigDetail')
        data_config = {
            "is_partial_ship": True,
            "is_picking": True
        }
        response = self.client.put(url_config, data_config, format='json')
        self.assertEqual(response.status_code, 200)
        self.config = data_config
        return response

    def create_delivery(self):
        sale_order = self.create_sale_order().data['result']
        sale_order_id = sale_order['id']
        delivery = OrderDelivery.objects.get_or_create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            sale_order_id=sale_order_id,
            from_picking_area='',
            customer_id=sale_order['customer']['id'],
            contact_id=sale_order['contact']['id'],
            kind_pickup=0 if self.config['is_picking'] else 1,
            sub=None,
            delivery_option=0 if not self.config['is_partial_ship'] else 1,
            state=0,
            delivery_quantity=1,
            delivered_quantity_before=0,
            remaining_quantity=1,
            ready_quantity=0,
            delivery_data=[],
            date_created=timezone.now()
        )
        obj_delivery = delivery[0]
        self.assertTrue(OrderDelivery.objects.filter(id=obj_delivery.id).exists())

        sub = OrderDeliverySub.objects.get_or_create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            code=obj_delivery.code,
            id=uuid4(),
            order_delivery_id=obj_delivery.id,
            date_done=None,
            previous_step=None,
            times=1,
            delivery_quantity=obj_delivery.delivery_quantity,
            delivered_quantity_before=0,
            remaining_quantity=obj_delivery.delivery_quantity,
            ready_quantity=obj_delivery.ready_quantity,
            delivery_data=[],
            is_updated=False,
            state=obj_delivery.state,
            sale_order_data=obj_delivery.sale_order_data,
            customer_data=obj_delivery.customer_data,
            contact_data=obj_delivery.contact_data,
            date_created=obj_delivery.date_created,
            config_at_that_point={
                "is_picking": self.config['is_picking'],
                "is_partial_ship": self.config['is_partial_ship']
            }
        )
        obj_sub = sub[0]
        self.assertTrue(OrderDeliverySub.objects.filter(id=obj_sub.id).exists())
        obj_delivery.sub = obj_sub
        obj_delivery.save(update_fields=["sub"])

        product_list = SaleOrderProduct.objects.select_related(
            'product', 'unit_of_measure'
        ).filter(
            sale_order_id=sale_order_id,
            product__isnull=False,
        )
        prod_create_list = []
        for item in product_list:
            temp = OrderDeliveryProduct(
                delivery_sub_id=obj_sub.id,
                product=item.product,
                product_data={
                    'id': str(item.product.id),
                    'title': str(item.product.title),
                    'code': str(item.product.code),
                    'remarks': ''
                } if item else {},
                uom=item.product.sale_default_uom,
                uom_data={
                    'id': str(item.product.sale_default_uom.id),
                    'title': str(item.product.sale_default_uom.title),
                    'code': str(item.product.sale_default_uom.code),
                } if item.product.sale_default_uom else {},

                delivery_quantity=item.product_quantity,
                delivered_quantity_before=0,
                remaining_quantity=item.product_quantity,
                ready_quantity=1,
                picked_quantity=0,
                order=1,
                is_promotion=False,
                product_unit_price=item.product_unit_price,
                product_tax_value=item.product_tax_value,
                product_subtotal_price=item.product_subtotal_price,
            )
            prod_create_list.append(temp)
        OrderDeliveryProduct.objects.bulk_create(prod_create_list)
        self.assertTrue(OrderDeliveryProduct.objects.filter(delivery_sub_id=obj_sub.id).exists())
        return obj_delivery, obj_sub

    def create_picking(self):
        if self.sale_order:
            sale_order = self.sale_order.data['result']
        else:
            sale_order = self.create_sale_order().data['result']
        sale_order_id = sale_order['id']
        warehouse = self.warehouse.data['result']
        picking = OrderPicking.objects.get_or_create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            sale_order_id=sale_order_id,
            ware_house_id=warehouse['id'],
            state=0,
            remarks="lorem ipsum",
            delivery_option=1,
            sub=None,
            pickup_quantity=1,
            picked_quantity_before=0,
            remaining_quantity=1,
            picked_quantity=0,
            date_created=timezone.now()
        )
        obj_picking = picking[0]
        self.assertTrue(OrderPicking.objects.filter(id=obj_picking.id).exists())

        sub = OrderPickingSub.objects.get_or_create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            code=obj_picking.code,
            id=uuid4(),
            order_picking_id=obj_picking.id,
            date_done=None,
            previous_step=None,
            times=1,
            pickup_quantity=obj_picking.pickup_quantity,
            picked_quantity_before=0,
            remaining_quantity=obj_picking.remaining_quantity,
            picked_quantity=0,
            ware_house_id=self.warehouse.data['result']['id'],
            state=obj_picking.state,
            sale_order_data=obj_picking.sale_order_data,
            date_created=obj_picking.date_created,
            config_at_that_point={
                "is_picking": self.config['is_picking'],
                "is_partial_ship": self.config['is_partial_ship']
            }
        )
        obj_sub = sub[0]
        self.assertTrue(OrderPickingSub.objects.filter(id=obj_sub.id).exists())
        obj_picking.sub = obj_sub
        obj_picking.save(update_fields=["sub"])

        product_list = SaleOrderProduct.objects.select_related(
            'product', 'unit_of_measure'
        ).filter(
            sale_order_id=sale_order_id,
            product__isnull=False,
        )
        prod_create_list = []
        for item in product_list:
            temp = OrderPickingProduct(
                picking_sub_id=obj_sub.id,
                product=item.product,
                product_data={
                    'id': str(item.product.id),
                    'title': str(item.product.title),
                    'code': str(item.product.code),
                    'remarks': ''
                } if item else {},
                uom=item.product.sale_default_uom,
                uom_data={
                    'id': str(item.product.sale_default_uom.id),
                    'title': str(item.product.sale_default_uom.title),
                    'code': str(item.product.sale_default_uom.code),
                } if item.product.sale_default_uom else {},

                pickup_quantity=1,
                picked_quantity_before=0,
                remaining_quantity=1,
                picked_quantity=0,
                order=1,
                is_promotion=False,
                product_unit_price=item.product_unit_price,
                product_tax_value=item.product_tax_value,
                product_subtotal_price=item.product_subtotal_price,
            )
            prod_create_list.append(temp)
        OrderPickingProduct.objects.bulk_create(prod_create_list)
        self.assertTrue(OrderPickingProduct.objects.filter(picking_sub_id=obj_sub.id).exists())
        return obj_picking, obj_sub

    def get_warehouse(self):
        url = reverse('WareHouseList')
        response = self.client.get(url, format='json')
        return response

    def create_new_warehouse(self):
        city = [item for item in self.get_city().data['result'] if item['title'] == 'TP Hồ Chí Minh']
        district = [item for item in self.get_district(city[0]['id']).data['result'] if item['title'] == 'Quận 7']
        ward = self.get_ward().data['result'][0]['id']

        url = reverse("WareHouseList")
        data = {
            'title': 'Kho lưu trữ số 2',
            'description': 'Lưu trữ linh kiện bán lẻ ở Tân Bình',
            'is_active': True,
            'address': 'chung cư DEF',
            'warehouse_type': 0,
            'full_address': 'chung cư DEF, Phường Phú Mỹ, Quận 7, TP Hồ Chí Minh',
            'city': city[0]['id'],
            'district': district[0]['id'],
            'ward': ward,
        }
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
            ['id', 'title', 'code', 'remarks', 'is_active', 'full_address', 'city', 'ward', 'district',
             'warehouse_type', 'agency', 'address'],
            check_sum_second=True,
        )
        return response

    def get_product_warehouse(self, warehouse_id=None):
        url = reverse('ProductWareHouseList')

        if warehouse_id:
            params = {
                'warehouse_id': warehouse_id
            }
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
        response = self.client.get(url, format='json')
        return response

    def test_create_goods_transfer(self):
        self.update_config_picking()
        _delivery, _delivery_sub = self.create_delivery()
        _picking, _picking_sub = self.create_picking()
        # _, _ = PickingDeliveryTestCase.test_2_complete_picking_delivery(self)
        new_warehouse = self.create_new_warehouse()
        products_warehouse = self.get_product_warehouse().data['result']

        data = {
            "title": "Goods transfer số 1",
            "note": "không note",
            "goods_transfer_type": 0,
            "date_transfer": "2023-09-29T10:40:35.299Z",
            "system_status": 0,
            "goods_transfer_datas": [
                {
                    "warehouse_product": products_warehouse[0]['id'],
                    "warehouse": products_warehouse[0]['warehouse'],
                    "end_warehouse": new_warehouse.data['result']['id'],
                    "uom": products_warehouse[0]['uom'],
                    "quantity": 10,
                    "unit_cost": products_warehouse[0]['unit_price'],
                    "subtotal": products_warehouse[0]['unit_price'] * 10,
                    "tax_data": products_warehouse[0]['tax_data'],
                    "unit_price": products_warehouse[0]['unit_price']
                }
            ]
        }
        url = reverse('GoodsTransferList')
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
            ['id', 'code', 'title', 'goods_transfer_type', 'date_transfer', 'system_status', 'agency', 'note',
             'goods_transfer_datas'],
            check_sum_second=True,
        )

        products_updated_1 = self.get_product_warehouse(products_warehouse[0]['warehouse'])
        products_updated_2 = self.get_product_warehouse(new_warehouse.data['result']['id'])
        self.assertEqual(
            response.data['result']['goods_transfer_datas'][0]['quantity'],
            products_warehouse[0]['stock_amount'] - products_updated_1.data['result'][0]['stock_amount']
        )
        self.assertEqual(
            response.data['result']['goods_transfer_datas'][0]['quantity'],
            products_updated_2.data['result'][0]['stock_amount']
        )
        return response

    def test_goods_transfer_list(self):
        self.test_goods_transfer_detail()
        url = reverse("GoodsTransferList")
        response = self.client.get(url, format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
        self.assertEqual(
            len(response.data['result']), 1
        )
        self.assertCountEqual(
            response.data['result'][0],
            ['id', 'code', 'title', 'goods_transfer_type', 'date_transfer', 'system_status'],
            check_sum_second=True,
        )
        return response

    def test_goods_transfer_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_goods_transfer()
            data_id = data_created.data['result']['id']
        url = reverse("GoodsTransferDetail", kwargs={'pk': data_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'code', 'title', 'goods_transfer_type', 'date_transfer', 'system_status', 'agency', 'note',
             'goods_transfer_datas'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_create_goods_issue(self):
        self.update_config_picking()
        _delivery, _delivery_sub = self.create_delivery()
        _picking, _picking_sub = self.create_picking()
        # _, _ = PickingDeliveryTestCase.test_2_complete_picking_delivery(self)
        products_warehouse = self.get_product_warehouse().data['result']
        url = reverse('GoodsIssueList')
        data = {
            "title": "Goods Issue test số 1",
            "date_issue": "2023-10-02T03:10:42.507Z",
            "note": "không có note",
            "goods_issue_type": 1,
            "goods_issue_datas": [
                {
                    "inventory_adjustment_item": None,
                    "product_warehouse": products_warehouse[0]['id'],
                    "warehouse": products_warehouse[0]['warehouse'],
                    "uom": products_warehouse[0]['uom'],
                    "description": "string",
                    "quantity": 10,
                    "unit_cost": 10000,
                    "subtotal": 100000,
                }
            ]
        }
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
            ['id', 'code', 'title', 'date_issue', 'note', 'goods_issue_type', 'system_status', 'goods_issue_datas',
             'inventory_adjustment', ],
            check_sum_second=True,
        )

        products_updated = self.get_product_warehouse()
        self.assertEqual(
            response.data['result']['goods_issue_datas'][0]['quantity'],
            products_warehouse[0]['stock_amount'] - products_updated.data['result'][0]['stock_amount']
        )
        return response

    def test_goods_issue_list(self):
        self.test_create_goods_issue()
        url = reverse("GoodsIssueList")
        response = self.client.get(url, format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
        self.assertEqual(
            len(response.data['result']), 1
        )
        self.assertCountEqual(
            response.data['result'][0],
            ['id', 'code', 'title', 'date_issue', 'goods_issue_type', 'system_status'],
            check_sum_second=True,
        )
        return response

    def test_goods_issue_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_goods_issue()
            data_id = data_created.data['result']['id']
        url = reverse("GoodsIssueDetail", kwargs={'pk': data_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'code', 'title', 'date_issue', 'note', 'goods_issue_type', 'system_status', 'goods_issue_datas',
             'inventory_adjustment', ],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response
