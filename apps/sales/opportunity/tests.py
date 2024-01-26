from django.urls import reverse
from rest_framework import status

from apps.masterdata.saledata.tests import ProductTestCase, TaxAndTaxCategoryTestCase, SalutationTestCase, \
    AccountGroupTestCase, IndustryTestCase, AccountTypeTestCase
from apps.shared.extends.tests import AdvanceTestCase, count_queries
from rest_framework.test import APIClient


# Create your tests here.


class TestCaseOpportunity(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

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

    def get_base_unit_measure(self):
        url = reverse('BaseItemUnitList')
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

    def get_price_list(self):
        url = reverse('PriceList')
        response = self.client.get(url, format='json')
        return response

    def get_currency(self):
        url = reverse('CurrencyList')
        response = self.client.get(url, format='json')
        return response

    def test_create_product(self):
        self.url = reverse("ProductList")
        product = ProductTestCase.test_create_product(self)
        return product

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def test_create_contact(self):
        url = reverse("ContactList")
        salutation = SalutationTestCase.test_create_new(self)
        employee = TestCaseOpportunity.get_employee(self)
        data = {
            "owner": employee.data['result'][0]['id'],
            "job_title": "Giám đốc nè",
            "biography": "không có",
            "fullname": "Trịnh Tuấn Nam",
            "salutation": salutation.data['result']['id'],
            "phone": "string",
            "mobile": "string",
            "email": "string",
            "report_to": None,
            "address_information": {},
            "additional_information": {},
            "account_name": None,
            "system_status": 0
        }

        response = self.client.post(url, data, format='json')
        return response

    def test_create_account(self):
        account_type = AccountTypeTestCase.test_get_account_type(self).data['result'][0]['id']
        account_group = AccountGroupTestCase.test_create_new(self).data['result']['id']
        employee = TestCaseOpportunity.get_employee(self).data['result'][0]['id']
        industry = IndustryTestCase.test_create_new(self).data['result']['id']

        data = {
            "name": "Công ty hạt giống, phân bón Trúc Phượng",
            "code": "AC01",
            "website": "trucphuong.com.vn",
            "account_type": [account_type],
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
        response = self.client.post(url, data, format='json')
        return response

    def test_create_opportunity(self):
        emp = TestCaseOpportunity.get_employee(self).data['result'][0]['id']
        customer = TestCaseOpportunity.test_create_account(self).data['result']['id']
        data = {
            "code": 'OPP001',
            "title": "Dự Án 1",
            "customer": customer,
            "product_category": [],
            "employee_inherit_id": emp
        }
        url = reverse("OpportunityList")
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
                'customer',
                'sale_person',
                'open_date',
                'quotation',
                'sale_order',
                'opportunity_sale_team_datas',
                'close_date',
                'stage',
                'is_close'
            ],
            check_sum_second=True,
        )

        return response

    @count_queries
    def test_get_list_opportunity(self):
        self.test_create_opportunity()
        self.max_queries_allowed = 15  # force 15 queries
        self.set_start_count_queries()
        url = reverse('OpportunityList')
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
            [
                'id',
                'title',
                'code',
                'customer',
                'sale_person',
                'open_date',
                'quotation',
                'sale_order',
                'opportunity_sale_team_datas',
                'close_date',
                'stage',
                'is_close'
            ],
            check_sum_second=True,
        )
        return response

    def test_get_detail_opportunity(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_opportunity()
            data_id = data_created.data['result']['id']
        url = reverse("OpportunityDetail", kwargs={'pk': data_id})
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
            [
                'id',
                'title',
                'code',
                'customer',
                'end_customer',
                'product_category',
                'budget_value',
                'open_date',
                'close_date',
                'decision_maker',
                'opportunity_product_datas',
                'total_product_pretax_amount',
                'total_product_tax',
                'total_product',
                'opportunity_competitors_datas',
                'opportunity_contact_role_datas',
                'win_rate',
                'is_input_rate',
                'customer_decision_factor',
                'sale_person',
                'stage',
                'lost_by_other_reason',
                'sale_order',
                'quotation',
                'is_close_lost',
                'is_deal_close',
                'members',
                'estimated_gross_profit_percent',
                'estimated_gross_profit_value'
            ],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_get_config(self):
        url = reverse('OpportunityConfigDetail')
        response = self.client.get(url, format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'is_select_stage', 'is_input_win_rate', 'is_account_manager_create'],
            check_sum_second=True,
        )
        return response

    def test_update_config(self):
        url = reverse('OpportunityConfigDetail')

        is_am_create = True
        data = {
            "is_select_stage": False,
            "is_input_win_rate": False,
            "is_account_manager_create": is_am_create
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_config()
        self.assertEqual(data_changed.data['result']['is_account_manager_create'], is_am_create)

        return response

    def test_create_factor(self):
        url = reverse('CustomerDecisionFactorList')
        data = {
            'title': 'Giá cao'
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
            ['id', 'title'],
            check_sum_second=True,
        )

        return response

    def test_delete_factor(self):
        data_created = self.test_create_factor()
        url = reverse('CustomerDecisionFactorDetail', kwargs={'pk': data_created.data['result']['id']})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        return response

    def test_create_stage(self):
        url = reverse('OpportunityConfigStageList')
        data = {
            'indicator': 'Stage Test',
            'description': 'Stage of Opp',
            'win_rate': 30,
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
            ['id', 'indicator', 'description', 'win_rate', 'logical_operator', 'condition_datas',
             'is_default', 'company', 'is_deal_closed', 'is_delivery', 'is_closed_lost', 'is_delete'],
            check_sum_second=True,
        )
        return response

    def test_get_list_stage(self):
        url = reverse('OpportunityConfigStageList')
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
            len(response.data['result']), 8
        )
        self.assertCountEqual(
            response.data['result'][0],
            ['id', 'indicator', 'description', 'win_rate', 'logical_operator', 'condition_datas',
             'is_default', 'company', 'is_deal_closed', 'is_delivery', 'is_closed_lost', 'is_delete'],
            check_sum_second=True,
        )
        return response

    def test_get_stage_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_stage()
            data_id = data_created.data['result']['id']
        url = reverse("OpportunityConfigStageDetail", kwargs={'pk': data_id})
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
            ['id', 'indicator', 'description', 'win_rate', 'logical_operator', 'condition_datas',
             'is_default', 'company', 'is_deal_closed', 'is_delivery', 'is_closed_lost', 'is_delete'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['indicator'], data_created.data['result']['indicator'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_update_stage(self):
        data_created = self.test_create_stage()
        url = reverse("OpportunityConfigStageDetail", kwargs={'pk': data_created.data['result']['id']})
        logical_operator = 1
        condition_datas = [
            {
                'condition_property': {
                    'id': 'e4e0c770-a0d1-492d-beae-3b31dcb391e1',
                    'title': 'Customer'
                },
                'comparison_operator': '≠',
                'compare_data': 0
            }
        ]
        win_rate = 45

        data = {
            'logical_operator': logical_operator,
            'condition_datas': condition_datas,
            'win_rate': win_rate,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_stage_detail(data_id=data_created.data['result']['id'])
        self.assertEqual(data_changed.data['result']['logical_operator'], logical_operator)
        self.assertEqual(data_changed.data['result']['condition_datas'], condition_datas)
        self.assertEqual(data_changed.data['result']['win_rate'], win_rate)
        return response

    def test_delete_stage(self):
        stage = self.test_create_stage()
        url = reverse("OpportunityConfigStageDetail", kwargs={'pk': stage.data['result']['id']})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        return response
