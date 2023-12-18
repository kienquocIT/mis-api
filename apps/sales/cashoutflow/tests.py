from django.urls import reverse
from rest_framework import status
from apps.masterdata.saledata.tests import IndustryTestCase, ExpenseItemTestCase, \
    TaxAndTaxCategoryTestCase
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


class AdvancePaymentTestCase(AdvanceTestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def test_ap_create(self):
        url = reverse("AdvancePaymentList")
        data1 = {
            'title': 'Tam ung thang 5',
            'sale_code_type': 2,  # non-sale
            'advance_payment_type': 0,  # to_employee
            'method': 1,  # bank
            'creator_name': self.get_employee().data['result'][0]['id'],
            'beneficiary': self.get_employee().data['result'][0]['id'],
            'return_date': '2023-06-06',
            'money_gave': True,
            'system_status': 1,
        }
        response1 = self.client.post(url, data1, format='json') # noqa
        self.assertResponseList(
            response1,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response1.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['result'],
            [
                'id',
                'title',
                'code',
                'method',
                'money_gave',
                'date_created',
                'return_date',
                'sale_code_type',
                'advance_value',
                'advance_payment_type',
                'expense_items',
                'opportunity_mapped',
                'quotation_mapped',
                'sale_order_mapped',
                'supplier',
                'creator_name',
                'employee_inherit',
                'workflow_runtime_id',
            ],
            check_sum_second=True,
        )
        return response1

    def test_ap_list(self):
        self.test_ap_create()
        url = reverse("AdvancePaymentList")
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
                'advance_payment_type',
                'date_created',
                'return_date',
                'status',
                'advance_value',
                'to_payment',
                'return_value',
                'remain_value',
                'money_gave',
                'creator_name_id',
                'employee_inherit_id',
                'sale_order_mapped',
                'quotation_mapped',
                'opportunity_mapped',
                'expense_items',
                'opportunity_id',
            ],
            check_sum_second=True,
        )
        return response

    def test_ap_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_ap_create()
            data_id = data_created.data['result']['id']
        url = reverse("AdvancePaymentDetail", kwargs={'pk': data_id})
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
                'method',
                'money_gave',
                'date_created',
                'return_date',
                'sale_code_type',
                'advance_value',
                'advance_payment_type',
                'expense_items',
                'opportunity_mapped',
                'quotation_mapped',
                'sale_order_mapped',
                'supplier',
                'creator_name',
                'employee_inherit',
                'workflow_runtime_id',
            ],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response


class PaymentTestCase(AdvanceTestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def create_new_account(self):
        # create industry
        url_create_industry = reverse('IndustryList')
        response_industry = self.client.post(
            url_create_industry,
            {
                'code': 'I00',
                'title': 'Banking0',
            },
            format='json'
        )

        # create account type
        url_create_account_type = reverse('AccountTypeList')
        response_account_type = self.client.post(
            url_create_account_type,
            {
                'code': 'AT00',
                'title': 'Service0',
            },
            format='json'
        )

        industry = response_industry.data['result']
        account_type = response_account_type.data['result']

        data = {  # noqa
            'name': 'FPT Shop',
            'code': 'PM000',
            'website': 'fptshop.com.vn',
            'tax_code': '35465785',
            'annual_revenue': '1',
            'total_employees': '1',
            'phone': '0903608494',
            'email': 'cuong@gmail.com',
            'industry': industry['id'],
            'manager': [self.get_employee().data['result'][0]['id']],
            'account_type': [account_type['id']],
            'account_type_selection': 0
        }
        url = reverse('AccountList')
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
                'id', 'name', 'website', 'code', 'account_type', 'manager', 'phone', 'shipping_address',
                'billing_address', 'parent_account_mapped', 'account_group', 'tax_code', 'industry', 'total_employees',
                'email', 'payment_term_customer_mapped', 'payment_term_supplier_mapped',
                'credit_limit_customer', 'credit_limit_supplier', 'currency', 'contact_mapped',
                'account_type_selection', 'bank_accounts_mapped', 'credit_cards_mapped',
                'annual_revenue', 'price_list_mapped', 'workflow_runtime_id', 'system_status'
            ],
            check_sum_second=True,
        )
        return response

    def create_config_payment_term(self):
        data = {
            'title': 'config payment term 01',
            'apply_for': 1,
            'remark': 'lorem ipsum dolor sit amet.',
            'term': [{"value": '100% sau khi ký HD', "unit_type": 1, "day_type": 1, "no_of_days": "1", "after": 1}],
        }
        url = reverse('ConfigPaymentTermList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def create_industry(self):
        response = IndustryTestCase.test_create_new(self)
        return response

    def get_account_type(self):
        url = reverse("AccountTypeList")
        response = self.client.get(url, format='json')
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
        payment_term = self.create_config_payment_term().data['result']['id']
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
        return response

    def test_payment_create(self):
        url = reverse("PaymentList")
        data1 = {
            'title': 'Thanh toan thang 5',
            'sale_code_type': 0,  # sale
            'sale_code_list': [
                {
                    'sale_code_id': self.create_sale_order().data['result']['id'],
                    'sale_code_detail': 2
                }
            ],
            'supplier': self.create_new_account().data['result']['id'],
            'method': 1,  # bank
            'creator_name': self.get_employee().data['result'][0]['id'],
            'beneficiary': self.get_employee().data['result'][0]['id'],
            'system_status': 1,
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertResponseList(
            response1,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response1.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['result'],
            [
                'id',
                'title',
                'code',
                'method',
                'date_created',
                'sale_code_type',
                'expense_items',
                'opportunity_mapped',
                'quotation_mapped',
                'sale_order_mapped',
                'supplier',
                'creator_name',
                'employee_inherit',
                'workflow_runtime_id',
                'system_status',
                'employee_payment',
                'is_internal_payment',
            ],
            check_sum_second=True,
        )

        return response1

    def test_payment_list(self):
        self.test_payment_create()
        url = reverse("PaymentList")
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
                'code',
                'title',
                'sale_code_type',
                'supplier',
                'method',
                'creator_name',
                'employee_inherit',
                'converted_value_list',
                'return_value_list',
                'payment_value',
                'date_created'
            ],
            check_sum_second=True,
        )
        return response

    def test_payment_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_payment_create()
            data_id = data_created.data['result']['id']
        url = reverse("PaymentDetail", kwargs={'pk': data_id})
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
                'method',
                'date_created',
                'sale_code_type',
                'expense_items',
                'opportunity_mapped',
                'quotation_mapped',
                'sale_order_mapped',
                'supplier',
                'creator_name',
                'employee_inherit',
                'workflow_runtime_id',
                'system_status',
                'employee_payment',
                'is_internal_payment',
            ],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response


class ReturnAdvanceTestCase(AdvanceTestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def test_create_new_tax_category(self):
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

    def test_ap_create(self):
        url = reverse("AdvancePaymentList")
        expense1, expense2 = ExpenseItemTestCase.test_create_new_expense(self)
        tax = TaxAndTaxCategoryTestCase.test_create_new_tax(self)
        data = {
            'title': 'Tam ung thang 5',
            'sale_code_type': 2,  # non-sale
            'advance_payment_type': 0,  # to_employee
            'supplier': None,
            'method': 1,  # bank
            'creator_name': self.get_employee().data['result'][0]['id'],
            'beneficiary': self.get_employee().data['result'][0]['id'],
            'return_date': '2024-06-06 11:21:00.000000',
            'money_gave': True,
            'expense_valid_list': [
                {
                    'expense_name': 'Expense Item so 1',
                    'expense_type_id': expense1.data['result']['id'],
                    'expense_tax_id': tax.data['result']['id'],
                    'expense_quantity': 2,
                    'expense_unit_price': 20000000,
                    'expense_tax_price': 20000000 * (tax.data['result']['rate']/100),
                    'expense_subtotal_price': 20000000,
                    'expense_after_tax_price': 20000000 + 20000000 * (tax.data['result']['rate']/100),
                    'expense_uom_name': 'manhour',
                }
            ],
            'system_status': 1,
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
            [
                'id',
                'title',
                'code',
                'method',
                'money_gave',
                'date_created',
                'return_date',
                'sale_code_type',
                'advance_value',
                'advance_payment_type',
                'expense_items',
                'opportunity_mapped',
                'quotation_mapped',
                'sale_order_mapped',
                'supplier',
                'creator_name',
                'employee_inherit',
                'system_status',
                'workflow_runtime_id',
            ],
            check_sum_second=True,
        )

        return response

    def test_create_return_advance(self):
        advance_payment = self.test_ap_create()
        employee_id = self.get_employee().data['result'][0]['id']
        url = reverse("ReturnAdvanceList")
        cost_data = []
        return_total = 0
        for item in advance_payment.data['result']['expense_items']:
            cost_data.append(
                {
                    'advance_payment_cost': item['id'],
                    'expense_name': item['expense_name'],
                    'expense_type': item['expense_type']['id'],
                    'remain_value': item['remain_total'],
                    'return_value': item['remain_total'],
                }
            )
            return_total += item['remain_total']

        data = {
            "title": 'Hoan ung thang 5',
            "advance_payment": advance_payment.data['result']['id'],
            "method": 0,
            "employee_created": employee_id,
            "employee_inherit_id": employee_id,
            "status": 0,
            "money_received": True,
            "cost": cost_data,
            "return_total": return_total,
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
            [
                'id', 'title', 'code', 'advance_payment', 'date_created', 'money_received',
                'employee_created', 'employee_inherit', 'method', 'status', 'cost', 'return_total'
            ],
            check_sum_second=True,
        )
        return response

    def test_create_return_advance_fail(self):
        advance_payment = self.test_ap_create()
        employee_id = self.get_employee().data['result'][0]['id']
        url = reverse("ReturnAdvanceList")
        cost_data = []
        return_total = 0
        for item in advance_payment.data['result']['expense_items']:
            cost_data.append(
                {
                    'advance_payment_cost': item['id'],
                    'expense_name': item['expense_name'],
                    'expense_type': item['expense_type']['id'],
                    'remain_value': item['remain_total'],
                    'return_value': item['remain_total'] + 500,
                }
            )
            return_total += item['remain_total']

        data = {  # noqa
            "title": 'Hoan ung thang 5',
            "advance_payment": '1',
            "method": 0,
            "employee_created": employee_id,
            "employee_inherit_id": employee_id,
            "status": 0,
            "money_received": True,
            "cost": cost_data,
            "return_total": return_total,
        }
        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            [
                'Input return', 'advance_payment'
            ],
            check_sum_second=True,
        )
        return response

    def test_get_list_return_advance(self):
        self.test_create_return_advance()
        url = reverse("ReturnAdvanceList")
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
                'id', 'title', 'code', 'advance_payment', 'date_created', 'money_received', 'status', 'return_total'
            ],
            check_sum_second=True,
        )
        return response

    def test_get_detail_return_advance(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_return_advance()
            data_id = data_created.data['result']['id']
        url = reverse("ReturnAdvanceDetail", kwargs={'pk': data_id})
        response = self.client.get(url, format='json')
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
                'id', 'code', 'title', 'advance_payment', 'employee_created', 'employee_inherit', 'method', 'status',
                'money_received', 'date_created', 'cost', 'return_total'
            ],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_update_return_advance(self):
        return_advance = self.test_create_return_advance()
        old_return_advance = self.test_get_detail_return_advance(return_advance.data['result']['id'])
        title_changed = 'Return advance update'
        product_data = old_return_advance.data['result']['cost']
        cost_data = []
        for item in product_data:
            cost_data.append({
                'advance_payment_cost': item['id'],
                'expense_name': item['expense_name'],
                'expense_type': item['expense_type']['id'],
                'remain_value': item['remain_total'],
                'return_value': item['return_value'] - 1,
            })
        data = {
            "title": title_changed,
            'advance_payment': old_return_advance.data['result']['advance_payment']['id'],
            "cost": cost_data,
        }
        url = reverse("ReturnAdvanceDetail", kwargs={'pk': return_advance.data['result']['id']})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_detail_return_advance(data_id=return_advance.data['result']['id'])
        self.assertEqual(
            data_changed.data['result']['cost'][0]['return_value'],
            old_return_advance.data['result']['cost'][0]['return_value']-1,
        )
        self.assertEqual(
            data_changed.data['result']['title'],
            title_changed
        )
        return response
