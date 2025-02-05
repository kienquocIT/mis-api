from django.utils.translation import gettext_lazy as trans

from .application_properties_params import (
    Quotation_data__params,
    Bastion_data_params,
    SaleOrder_data__params,
    AdvancePayment_data__params,
    Payment_data__params,
    IA_data__params,
    Goods_Transfer_data__params,
    Goods_Return_data__params, Delivery_data__params, Bidding_data__params
)

__all__ = ["ApplicationProperty_data"]

AppProp_SaleData_Contact_data = {
    # 828b785a-8f57-4a03-9f90-e0edf96560d7 # SaleData.Contact
    "1732206e-c2f4-42bf-98c2-9cc3d5294de6": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Owner",
        "code": "owner",
        "type": 5,
        "content_type": "hr.Employee",
        "is_filter_condition": True,
    },
    "3e9235f9-e7d0-4b9c-87ce-ad3e66aa41c2": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Job Title",
        "code": "job_title",
        "type": 1,
        "is_filter_condition": True,
    },
    "1fea72e9-542b-48d3-adb1-5516b931160f": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Biography",
        "code": "biography",
        "type": 1,
    },
    "e0f5900c-0723-4f75-b614-18e4b5b060f3": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Avatar",
        "code": "avatar",
        "type": 1,
    },
    "e762cb70-d7d9-4500-88c8-0144f35576c6": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Fullname",
        "code": "fullname",
        "type": 1,
        "is_filter_condition": True,
    },
    "938f4ae5-9bcf-40c2-97bb-fc949b55e700": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Salutation",
        "code": "salutation",
        "type": 5,
        "content_type": "saledata_Salutation",
    },
    "33dd2595-9974-4c21-bba0-374eb31decdc": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Phone",
        "code": "phone",
        "type": 1,
    },
    "7f3fe89f-8168-47f9-8a88-ee344012d220": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Mobile",
        "code": "mobile",
        "type": 1,
    },
    "3dfdbdf3-4abc-4955-bef5-e2ba543887d1": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Email",
        "code": "email",
        "type": 1,
    },
    "6b2c8c9c-d640-4c4b-9933-e5810c8b8889": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Report To",
        "code": "report_to",
        "type": 5,
        "content_type": "saledata_Contact",
    },
    "7744b2e9-b5e3-459e-85ad-5145f0b0e775": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Address Information",
        "code": "address_information",
        "type": 1,
    },
    "e35b22d1-e5a4-4d75-a5b3-e152aa32026d": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Additional Information",
        "code": "additional_information",
        "type": 1,
    },
    "a6a64634-2cf7-41f8-a6fd-3f8f2fae77d2": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Account Name",
        "code": "account_name",
        "type": 5,
        "content_type": "saledata.Account",
    },
    "1fcbed18-b635-4d53-a91a-ef914dc7d310": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Owner name",
        "code": "contact__owner__name",
        "type": 1,
        "is_filter_condition": True,
    },
}

AppProp_SaleData_Account_data = {
    # 4e48c863-861b-475a-aa5e-97a4ed26f294 # SaleData.Account
    "6609da8f-66d0-4d90-ba20-711ef6e8e49e": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Name",
        "code": "name",
        "is_filter_condition": True,
        "type": 1,
    },
    "8937c428-66dd-4c97-a325-88bae5d68056": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Website",
        "code": "website",
        "type": 1,
    },
    "6f1f4f1f-1b92-47c2-b42a-6ed2119e08f7": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Account Type",
        "code": "account_type",
        "type": 1,
    },
    "27db08f5-8469-4ef1-9ec6-df7811cf7540": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Account Owner",
        "code": "owner",
        "type": 5,
        "content_type": "saledata.Contact",
        "is_filter_condition": True,
    },
    "f2b81fd6-3657-448b-b93b-0b9552fd0f3e": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Account Manager",
        "code": "manager",
        "type": 1,
        "is_filter_condition": True,
    },
    "30490c0b-69f8-49c3-a79e-0a466b3f20da": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Account Group",
        "code": "account_group",
        "type": 5,
        "content_type": "saledata.AccountGroup",
        "is_filter_condition": False,
    },
    "64dca30b-2a99-4135-9349-a739b0b83ef7": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Tax Code",
        "code": "tax_code",
        "type": 1,
    },
    "f743952a-f39e-4203-a123-0823606628a1": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Industry",
        "code": "industry",
        "type": 5,
        "content_type": "saledata.Industry",
        "is_filter_condition": True,
    },
    "bb05d49e-4825-43cf-81c1-633a03a4a1ab": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Annual Revenue",
        "code": "annual_revenue",
        "type": 3,
    },
    "3f7667e0-15a7-49f5-ba49-50d4ce8ca0df": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Revenue YTD",
        "code": "revenue_ytd",
        "type": 6,
        "is_filter_condition": True,
    },
    "8d079e31-323a-46c5-97bb-dcfe1278e356": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Total Employees",
        "code": "total_employees",
        "type": 3,
    },
    "196c67ce-1c48-446a-ae81-e40b24d83cd3": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Phone",
        "code": "phone",
        "type": 1,
    },
    "ce285eae-b1b7-4edd-af9e-d699cdf1f130": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Email",
        "code": "email",
        "type": 1,
        "is_filter_condition": True,
    },
    "ad5561aa-b3aa-49d2-8282-2d8b7a277929": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Currency",
        "code": "currency",
        "type": 5,
        "content_type": "saledata.Currency",
        "is_filter_condition": False,
    },
    "b0b2ca8d-659b-46da-81b8-449f0fcf8acf": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Shipping Address",
        "code": "account_mapped_shipping_address__full_address",
        "type": 1,
        "is_filter_condition": True,
    },
    "0d3511e9-7d86-4d4c-a249-f43a0144b406": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Billing Address",
        "code": "billing_address",
        "type": 1,
    },
    "dff7b13f-67d2-45a6-b4ff-b4aa40d7dcde": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Payment Term",
        "code": "payment_term_mapped",
        "type": 5,
        "content_type": "saledata.PaymentTerm",
    },
    "208d94a5-8756-4f45-ae14-184a035bc33d": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Price list",
        "code": "price_list_mapped",
        "type": 5,
        "content_type": "saledata.Price",
    },
    "9a7e9c1e-7b41-409c-802e-b60473023017": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Credit Limit Supplier",
        "code": "credit_limit_supplier",
        "type": 6,
    },
    "9a42a3a8-0b5b-4188-ace5-21c09df5a13a": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Credit Limit Customer",
        "code": "credit_limit_customer",
        "type": 6,
    },
    "41b9f085-9510-4163-90c1-cd3249ded458": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Bank Accounts Information",
        "code": "bank_accounts_information",
        "type": 1,
    },
    "7b5803b4-2f40-4149-9c9d-4229ee6ad51f": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Credit Cards Information",
        "code": "credit_cards_information",
        "type": 1,
    },
    "5ca5ca1e-010a-48d2-810d-62ddc0d2da69": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Account Type Selection",
        "code": "account_type_selection",
        "type": 3,
    },
    "a08a0a2f-24cb-4baf-aac5-33464e6eb0da": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Number of Opening Opportunities",
        "code": "open_opp_num",
        "type": 6,
        "is_filter_condition": True,
    },
    "688fccc3-b344-4bcc-83ad-b3f421cd6541": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Last Contacted For Open Opportunities (days)",
        "code": "last_contacted_open_opp",
        "type": 6,
        "is_filter_condition": True,
    },
    "037a4a83-08b1-4694-91dc-de021c14989e": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Current Opportunity Stage",
        "code": "curr_opp_stage",
        "type": 5,
        "is_filter_condition": True,
        "content_type": "opportunity.OpportunityConfigStage",
    },
    "a409dcd8-7f79-406f-b68e-fa6846862e4c": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Account Owner name",
        "code": "owner__fullname",
        "type": 1,
        "is_filter_condition": True,
    },
    "f8ccf26e-f35c-4cd4-a94b-70b89e632510": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Number of Sale Orders (Total)",
        "code": "num_sale_orders",
        "type": 6,
        "is_filter_condition": True,
    },
}

AppProp_SaleData_Quotation_data = {
    # b9650500-aba7-44e3-b6e0-2542622702a3 # quotation.Quotation
    # General fields
    'd59eea03-2eb8-4d1a-ac9d-dc3993545b67': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Opportunity')),
        'code': 'opportunity_id',
        'type': 5,
        'content_type': 'opportunity.opportunity',
    },
    '76f10bb2-016a-47a9-83b0-4796a96c9d07': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Contact')),
        'code': 'contact',
        'type': 5,
        'content_type': 'saledata.contact',
    },
    '8f3fabc0-ffbe-409a-9894-2d2c36993cc8': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Payment term')),
        'code': 'payment_term',
        'type': 5,
        'content_type': 'saledata.paymentterm',
    },
    'a77ab96c-1141-4915-a7d4-ed29874d7c7c': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Customer confirm')),
        'code': 'is_customer_confirm',
        'type': 4,
    },
    'd47555f5-b6e5-420f-996e-31d8600825fa': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Print document')),
        'code': 'print_document',
        'type': 4,
    },
    # Totals of products
    '06c2414c-ac31-4f16-b0ac-edd0b8d54ded': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total product pretax amount')),
        'code': 'total_product_pretax_amount',
        'remark': 'Total product pretax amount of quotation',
        'parent_n_id': 'b426fe8e-c58d-482b-aba8-3f986e3b5768',  # tab detail
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': False,
    },
    'efd2c678-dadf-4f77-be5f-9cea9598c017': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total product discount rate')),
        'code': 'total_product_discount_rate',
        'remark': 'Total product discount rate of quotation',
        'parent_n_id': 'b426fe8e-c58d-482b-aba8-3f986e3b5768',  # tab detail
        'type': 6,
    },
    '9dc78b54-0afb-4f53-af42-5ef059451ad3': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total product discount')),
        'code': 'total_product_discount',
        'remark': 'Total product discount of quotation',
        'parent_n_id': 'b426fe8e-c58d-482b-aba8-3f986e3b5768',  # tab detail
        'type': 6,
    },
    'ced7e425-d284-4f1c-ada4-45f62636b5da': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total product tax')),
        'code': 'total_product_tax',
        'remark': 'Total product tax of quotation',
        'parent_n_id': 'b426fe8e-c58d-482b-aba8-3f986e3b5768',  # tab detail
        'type': 6,
    },
    'bd9374ec-cdc7-4d95-9ece-363b3b623d3b': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total product')),
        'code': 'total_product',
        'remark': 'Total product of quotation',
        'parent_n_id': 'b426fe8e-c58d-482b-aba8-3f986e3b5768',  # tab detail
        'type': 6,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'b398bec4-a122-44b9-92fe-642d869e9238': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total product revenue before tax')),
        'code': 'total_product_revenue_before_tax',
        'remark': 'Total product revenue before tax of quotation',
        'parent_n_id': 'b426fe8e-c58d-482b-aba8-3f986e3b5768',  # tab detail
        'type': 6,
    },
    # Totals of costs
    'dcce7fbe-2cb0-4306-97a7-73a644b0c799': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total cost pretax amount')),
        'code': 'total_cost_pretax_amount',
        'remark': 'Total cost pretax amount of quotation',
        'parent_n_id': 'cf82dbac-a903-425c-aa41-b45e7ccec41b',  # tab cost
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': False,
    },
    '619f3301-48e2-476b-8a85-b5998ccd3e4a': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total cost tax')),
        'code': 'total_cost_tax',
        'remark': 'Total cost tax of quotation',
        'parent_n_id': 'cf82dbac-a903-425c-aa41-b45e7ccec41b',  # tab cost
        'type': 6,
    },
    'd3ce455f-9ea7-42c0-87b4-5536b437cdd5': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total cost')),
        'code': 'total_cost',
        'remark': 'Total cost of quotation',
        'parent_n_id': 'cf82dbac-a903-425c-aa41-b45e7ccec41b',  # tab cost
        'type': 6,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    # Totals of expenses
    '5a6e8904-c39c-4e45-aed9-7b989299f593': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total expense pretax amount')),
        'code': 'total_expense_pretax_amount',
        'remark': 'Total expense pretax amount of quotation',
        'parent_n_id': '10946df3-1e9d-4538-9173-7f75861ab7ed',  # tab expense
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': False,
    },
    '7fcbe504-de29-4600-a748-05639db2841c': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total expense tax')),
        'code': 'total_expense_tax',
        'remark': 'Total expense tax of quotation',
        'parent_n_id': '10946df3-1e9d-4538-9173-7f75861ab7ed',  # tab expense
        'type': 6,
    },
    '6d02b18b-3e5c-485f-8c99-00101e0af87f': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total expense')),
        'code': 'total_expense',
        'remark': 'Total expense of quotation',
        'parent_n_id': '10946df3-1e9d-4538-9173-7f75861ab7ed',  # tab expense
        'type': 6,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    # WORKFLOW
    '0b6765ec-be8f-4982-8dc3-fd90f91d941c': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Title')),
        'code': 'title',
        'type': 1,
        'is_print': True,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    '37891f62-57f9-436e-9f93-caa1b6556590': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Salesperson')),
        'code': 'employee_inherit_id',
        'type': 5,
        'content_type': 'hr.employee',
        'is_wf_zone': True,
        'is_wf_condition': True,
    },
    'b86ac087-8c67-4291-b01f-946803954937': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Customer')),
        'code': 'customer_data__id',
        'type': 5,
        'content_type': 'saledata.account',
        'is_wf_zone': True,
        'is_wf_condition': True,
    },
    'de534b7e-e653-48c4-9538-ec8b5f4b5ec0': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Industry')),
        'code': 'customer_data__industry__id',
        'type': 5,
        'content_type': 'saledata.industry',
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    'b426fe8e-c58d-482b-aba8-3f986e3b5768': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Tab product')),
        'code': 'quotation_products_data',
        'remark': 'Tab line detail of quotation',
        'code_related': [
            'quotation_costs_data', 'quotation_indicators_data',
            'total_cost_pretax_amount', 'total_cost_tax', 'total_cost'
        ],
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'fda17a32-9f16-4e7c-b7db-53f007f6467b': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Tab logistic')),
        'code': 'quotation_logistic_data',
        'remark': 'Tab logistic of quotation',
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'cf82dbac-a903-425c-aa41-b45e7ccec41b': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Tab cost')),
        'code': 'quotation_costs_data',
        'remark': 'Tab cost of quotation',
        'code_related': ['quotation_indicators_data'],
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    '10946df3-1e9d-4538-9173-7f75861ab7ed': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Tab expense')),
        'code': 'quotation_expenses_data',
        'remark': 'Tab expense of quotation',
        'code_related': ['quotation_indicators_data'],
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'd846692b-9d65-4dcb-a667-4318cae17a18': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Tab indicator')),
        'code': 'quotation_indicators_data',
        'remark': 'Tab indicator of quotation',
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    '47e31f9e-69a3-4b69-ada3-ce777c420864': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product')),
        'code': 'quotation_products_data__product_data__id',
        'type': 5,
        'content_type': 'saledata.product',
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    '42cc882b-15af-4034-b8a1-0d8d6038d537': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product type')),
        'code': 'quotation_products_data__product_data__general_information__product_type__id',
        'type': 5,
        'content_type': 'saledata.producttype',
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    '54c2b111-0f31-41f8-a8aa-d095aad4c90a': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Revenue')),
        'code': 'indicator_revenue',
        'remark': 'Indicator revenue of quotation',
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    '1b61ecbc-99cf-43ac-bd1a-2cd15f91934b': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Gross profit')),
        'code': 'indicator_gross_profit',
        'remark': 'Indicator gross profit of quotation',
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    'cb9cc655-2c94-42ea-835a-4580379c5fc2': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Net income')),
        'code': 'indicator_net_income',
        'remark': 'Indicator net income of quotation',
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    # INDICATOR
    '89621079-c323-4ef8-8b67-a713e40e5680': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product')),
        'code': 'product_data__title',
        'remark': 'Sản phẩm trong thông tin tab sản phẩm',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.product',
        'example': 'prop(Product)=="Laptop"',
        'date_created': '2025-01-01 00:00:16',
    },
    'f0ae96de-d51f-421e-87e1-4ee150095fc9': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product type')),
        'code': 'product_data__general_information__product_type__title',
        'remark': 'Loại sản phẩm trong thông tin tab sản phẩm',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.producttype',
        'example': 'prop(Product type)=="Dịch vụ"',
        'date_created': '2025-01-01 00:00:15',
    },
    '9645bb94-53cd-490f-902c-9878370a08aa': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product category')),
        'code': 'product_data__general_information__product_category__title',
        'remark': 'Danh mục sản phẩm trong thông tin tab sản phẩm',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.productcategory',
        'example': 'prop(Product category)=="Điện tử"',
        'date_created': '2025-01-01 00:00:15',
    },
    '73a627ef-016a-4497-ae9f-0ba92e0f721d': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product quantity')),
        'code': 'product_quantity',
        'remark': 'Số lượng của một dòng sản phẩm',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Product quantity)',
        'date_created': '2025-01-01 00:00:14',
    },
    '67100057-ee5b-46ef-958f-5c15e5c5e5e2': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product unit price')),
        'code': 'product_unit_price',
        'remark': 'Đơn giá của một dòng sản phẩm',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Product unit price)',
        'date_created': '2025-01-01 00:00:13',
    },
    '016a8435-b564-45cb-99b6-dae38d2df5f2': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Product subtotal')),
        'code': 'product_subtotal_price',
        'remark': 'Thành tiển của một dòng sản phẩm',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Product subtotal)',
        'date_created': '2025-01-01 00:00:12',
    },
    '8ecc50e2-e7d6-4b0d-9cd5-92eec83f8f95': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Expense type')),
        'code': 'expense_item_data__title',
        'remark': 'Loại chi phí trong thông tin tab chi phí',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.expenseitem',
        'example': 'prop(Expense type)=="Deployment expense"',
        'date_created': '2025-01-01 00:00:11',
    },
    'af3d550c-8b22-481f-998b-35499f0df141': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Labor expense type')),
        'code': 'expense_data__title',
        'remark': 'Loại chi phí nhân công trong thông tin tab chi phí',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.expense',
        'example': 'prop(Labor expense type)=="Deployment manday"',
        'date_created': '2025-01-01 00:00:10',
    },
    '195479c7-cf10-463f-95fb-8784f47041df': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Expense quantity')),
        'code': 'expense_quantity',
        'remark': 'Số lượng của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Expense quantity)',
        'date_created': '2025-01-01 00:00:09',
    },
    'ad5ca6e1-8788-40ce-acac-9850a49a6565': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Expense unit price')),
        'code': 'expense_price',
        'remark': 'Đơn giá của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Expense unit price)',
        'date_created': '2025-01-01 00:00:08',
    },
    'f0251c13-0480-4ac1-94d3-ebe03afb93bf': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Expense subtotal before tax')),
        'code': 'expense_subtotal_price',
        'remark': 'Thành tiền của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Expense subtotal before tax)',
        'date_created': '2025-01-01 00:00:07',
    },
    '6c6af508-c5b0-4295-b92a-bfc53dfad9d3': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Expense subtotal after tax')),
        'code': 'expense_subtotal_price_after_tax',
        'remark': 'Thành tiền sau thuế của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Expense subtotal after tax)',
        'date_created': '2025-01-01 00:00:06',
    },
    'd0c18f0b-2ab6-4fa1-bd77-e627e606ce3f': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total revenue after tax')),
        'code': 'total_product',
        'remark': 'Total revenue of quotation',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Total revenue after tax)',
        'date_created': '2025-01-01 00:00:05',
    },
    '148843b4-97a9-47ea-a5cf-a5cf1d557abd': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total cost after tax')),
        'code': 'total_cost',
        'remark': 'Total cost of quotation',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Total cost after tax)',
        'date_created': '2025-01-01 00:00:04',
    },
    '78584833-3ad3-406a-8969-749e2c9b899c': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total expense after tax')),
        'code': 'total_expense',
        'remark': 'Total expense of quotation',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Total expense after tax)',
        'date_created': '2025-01-01 00:00:03',
    },
    '9a8bef37-6812-4d8b-ba6a-dc5669e61029': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total revenue before tax')),
        'code': 'total_product_revenue_before_tax',
        'remark': 'Total revenue before tax of quotation (after discount on total, apply promotion,...)',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Total revenue before tax)',
        'date_created': '2025-01-01 00:00:02',
    },
    'd1dcd149-6fc8-4234-870d-29497f8cfb88': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total cost before tax')),
        'code': 'total_cost_pretax_amount',
        'remark': 'Total cost before tax of quotation',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Total cost before tax)',
        'date_created': '2025-01-01 00:00:01',
    },
    '490ecfee-30d2-468a-b075-84d44b8b150e': {
        'application_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
        'title': str(trans('Total expense before tax')),
        'code': 'total_expense_pretax_amount',
        'remark': 'Total expense before tax of quotation',
        'type': 6,
        'is_sale_indicator': True,
        'example': 'prop(Total expense before tax)',
        'date_created': '2025-01-01 00:00:00',
    },
    # PRINT
    **Quotation_data__params,
}

AppProp_SaleData_Opportunity_data = {
    # 296a1410-8d72-46a8-a0a1-1821f196e66c # Opportunity.Opportunity
    'e4e0c770-a0d1-492d-beae-3b31dcb391e1': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Customer',
        'code': 'customer',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None
                },
                {
                    'id': 1,
                    'value': '1-10 billions'
                },
                {
                    'id': 2,
                    'value': '10-20 billions'
                },
                {
                    'id': 3,
                    'value': '20-50 billions'
                },
                {
                    'id': 4,
                    'value': '50-200 billions'
                },
                {
                    'id': 5,
                    'value': '200-1000 billions'
                },
                {
                    'id': 6,
                    'value': '> 1000 billions'
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    '496aca60-bf3d-4879-a4cb-6eb1ebaf4ce8': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Product Category',
        'code': 'product_category',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    '36233e9a-8dc9-4a7c-a6ad-504bac91d4cb': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Budget',
        'code': 'budget',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    '195440c2-41bc-43f1-b387-fc5cd26401df': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Open Date',
        'code': 'open_date',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    '43009b1a-a25d-43be-ab97-47540a2f00cb': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Close Date',
        'code': 'close_date',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    '35dbf6f2-78a8-4286-8cf3-b95de5c78873': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Decision maker',
        'code': 'decision_maker',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    '92c8035a-5372-41c1-9a8e-4b048d8af406': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Lost By Other Reason',
        'code': 'lost_by_other_reason',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': 'checked',
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': 'checked',
                }
            ]
        }
    },
    '39b50254-e32d-473b-8380-f3b7765af434': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Product.Line.Detail',
        'code': 'product_line_detail',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    'c8fa79ae-2490-4286-af25-3407e129fedb': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Competitor.Win',
        'code': 'competitor_win',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    'acab2c1e-74f2-421b-8838-7aa55c217f72': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Quotation.confirm',
        'code': 'quotation_confirm',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': True,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': True,
                }
            ]
        }
    },
    '9db4e835-c647-4de5-aa1c-43304ddeccd1': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'SaleOrder.status',
        'code': 'sale_order_status',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': 'Approved',
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': 'Approved',
                }
            ]
        }
    },
    'b5aa8550-7fc5-4cb8-a952-b6904b2599e5': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'SaleOrder.Delivery.Status',
        'code': 'sale_order_delivery_status',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': None,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': None,
                }
            ]
        }
    },
    'f436053d-f15a-4505-b368-9ccdf5afb5f6': {
        'application_id': '296a1410-8d72-46a8-a0a1-1821f196e66c',
        'title': 'Close Deal',
        'code': 'close_deal',
        'type': 1,
        "content_type": "sales_opportunity",
        'opp_stage_operator': ['=', '≠'],
        'stage_compare_data': {
            '=': [
                {
                    'id': 0,
                    'value': True,
                }
            ],
            '≠': [
                {
                    'id': 0,
                    'value': True,
                }
            ]
        }
    },
}

AppProp_SaleData_SaleOrder_data = {
    # a870e392-9ad2-4fe2-9baa-298a38691cf2 # saleorder.SaleOrder
    # General fields
    '031519a6-3c40-4eb2-845a-32f869a2e903': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Opportunity')),
        'code': 'opportunity_id',
        'type': 5,
        'content_type': 'opportunity.opportunity',
    },
    '77357c24-b809-42bf-a190-f216d3df7206': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Contact')),
        'code': 'contact',
        'type': 5,
        'content_type': 'saledata.contact',
    },
    '60464a8f-5261-4446-940f-69746784dc6a': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Payment term')),
        'code': 'payment_term',
        'type': 5,
        'content_type': 'saledata.paymentterm',
    },
    # Totals of products
    '9ebf66f9-2a2b-4343-98bd-4b2b6b4e1425': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total product pretax amount')),
        'code': 'total_product_pretax_amount',
        'remark': 'Total product pretax amount of sale order',
        'parent_n_id': '50857b72-4bc2-4d26-a365-9ee1e894b6d2',  # tab detail
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': False,
    },
    'c2197be7-35a2-4efc-afb3-56feaf969957': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total product discount rate')),
        'code': 'total_product_discount_rate',
        'remark': 'Total product discount rate of sale order',
        'parent_n_id': '50857b72-4bc2-4d26-a365-9ee1e894b6d2',  # tab detail
        'type': 6,
    },
    '923da4a7-5b53-4961-ab59-4a7cac711631': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total product discount')),
        'code': 'total_product_discount',
        'remark': 'Total product discount of sale order',
        'parent_n_id': '50857b72-4bc2-4d26-a365-9ee1e894b6d2',  # tab detail
        'type': 6,
    },
    '172102c3-43af-4114-b9da-ca3627e38b70': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total product tax')),
        'code': 'total_product_tax',
        'remark': 'Total product tax of sale order',
        'parent_n_id': '50857b72-4bc2-4d26-a365-9ee1e894b6d2',  # tab detail
        'type': 6,
    },
    'cd11b1b0-efd4-45c0-8037-a8f9af5b8785': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total product')),
        'code': 'total_product',
        'remark': 'Total product of sale order',
        'parent_n_id': '50857b72-4bc2-4d26-a365-9ee1e894b6d2',  # tab detail
        'type': 6,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    '3a3ce0bc-8c67-4558-9812-8a6dbf45cf88': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total product revenue before tax')),
        'code': 'total_product_revenue_before_tax',
        'remark': 'Total product revenue before tax of sale order',
        'parent_n_id': '50857b72-4bc2-4d26-a365-9ee1e894b6d2',  # tab detail
        'type': 6,
    },
    # Totals of costs
    'e58c5ade-6520-4c35-ae6e-83703578f33b': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total cost pretax amount')),
        'code': 'total_cost_pretax_amount',
        'remark': 'Total cost pretax amount of sale order',
        'parent_n_id': '0cb516c2-2b59-4a11-98cf-4b78fd4a464d',  # tab cost
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': False,
    },
    'f56243a9-4821-40fa-83b9-ff48a7c807f7': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total cost tax')),
        'code': 'total_cost_tax',
        'remark': 'Total cost tax of sale order',
        'parent_n_id': '0cb516c2-2b59-4a11-98cf-4b78fd4a464d',  # tab cost
        'type': 6,
    },
    'ad38f62e-31d3-48e7-8c23-42e127aeb3d8': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total cost')),
        'code': 'total_cost',
        'remark': 'Total cost of sale order',
        'parent_n_id': '0cb516c2-2b59-4a11-98cf-4b78fd4a464d',  # tab cost
        'type': 6,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    # Totals of expenses
    '23a82e99-aa8e-47c3-b8b1-3ac3038d9b04': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total expense pretax amount')),
        'code': 'total_expense_pretax_amount',
        'remark': 'Total expense pretax amount of sale order',
        'parent_n_id': '4ac8ebc5-adfd-4078-9834-51de58c064d1',  # tab expense
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': False,
    },
    '4365f9bd-5c84-46d7-a995-c54e0878ca59': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total expense tax')),
        'code': 'total_expense_tax',
        'remark': 'Total expense tax of sale order',
        'parent_n_id': '4ac8ebc5-adfd-4078-9834-51de58c064d1',  # tab expense
        'type': 6,
    },
    '0b0bac8a-9572-4cae-8a57-cc09f2262b8b': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total expense')),
        'code': 'total_expense',
        'remark': 'Total expense of sale order',
        'parent_n_id': '4ac8ebc5-adfd-4078-9834-51de58c064d1',  # tab expense
        'type': 6,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    # WORKFLOW
    '81f37376-b62a-4dd9-bc97-50c5c49ba4fe': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Title')),
        'code': 'title',
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'fa8df51a-fb69-4887-9de4-e5e3c933d3b5': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Salesperson')),
        'code': 'employee_inherit_id',
        'type': 5,
        'content_type': 'hr.employee',
        'is_wf_zone': True,
        'is_wf_condition': True,
    },
    'b24e175d-4faf-4689-ae8f-aba3972ac70f': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Customer')),
        'code': 'customer_data__id',
        'type': 5,
        'content_type': 'saledata.account',
        'is_wf_zone': True,
        'is_wf_condition': True,
    },
    '7b390a4d-58ec-490f-91d3-f2fbbd0d3d2b': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Industry')),
        'code': 'customer_data__industry__id',
        'type': 5,
        'content_type': 'saledata.industry',
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    '50857b72-4bc2-4d26-a365-9ee1e894b6d2': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Tab detail')),
        'code': 'sale_order_products_data',
        'remark': 'Tab line detail of sale order',
        'code_related': [
            'sale_order_costs_data', 'sale_order_indicators_data',
            'total_cost_pretax_amount', 'total_cost_tax', 'total_cost'
        ],
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'd13549a8-a1c1-450e-818a-613cde814d6a': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Tab logistic')),
        'code': 'sale_order_logistic_data',
        'remark': 'Tab logistic of sale order',
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    '0cb516c2-2b59-4a11-98cf-4b78fd4a464d': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Tab cost')),
        'code': 'sale_order_costs_data',
        'remark': 'Tab cost of sale order',
        'code_related': ['sale_order_indicators_data'],
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    '4ac8ebc5-adfd-4078-9834-51de58c064d1': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Tab expense')),
        'code': 'sale_order_expenses_data',
        'remark': 'Tab expense of sale order',
        'code_related': ['sale_order_indicators_data'],
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'c12b9e32-1043-492c-ac33-78e838c43aac': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Tab indicator')),
        'code': 'sale_order_indicators_data',
        'remark': 'Tab indicator of sale order',
        'type': 1,
        'is_wf_zone': True,
        'is_wf_condition': False,
    },
    'de2717ad-b461-4b7a-a29c-63baf1e0f632': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product')),
        'code': 'sale_order_products_data__product_data__id',
        'type': 5,
        'content_type': 'saledata.product',
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    'ded465fa-2ed9-48a8-9e70-ba72e8a011d2': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product type')),
        'code': 'sale_order_products_data__product_data__general_information__product_type__id',
        'type': 5,
        'content_type': 'saledata.producttype',
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    '34fa41c9-3cce-4178-bf13-e1499fe5afd3': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Revenue')),
        'code': 'indicator_revenue',
        'remark': 'Indicator revenue of sale order',
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    '33bcecce-b94a-45f8-b5b6-d4f27e36ee34': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Gross profit')),
        'code': 'indicator_gross_profit',
        'remark': 'Indicator gross profit of sale order',
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    'f316faea-3199-4448-a214-18c56cfde2d7': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Net income')),
        'code': 'indicator_net_income',
        'remark': 'Indicator net income of sale order',
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
    # INDICATOR
    'e43e140e-beb1-49f0-a776-404c491fc1da': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product')),
        'code': 'product_data__title',
        'remark': 'Sản phẩm trong thông tin tab sản phẩm',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.product',
        'example': 'prop(Product)=="Laptop"',
        'date_created': '2025-01-01 00:00:16',
    },
    '43d04cd8-a595-4d03-8b6f-9c6eb2c3e343': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product type')),
        'code': 'product_data__general_information__product_type__title',
        'remark': 'Loại sản phẩm trong thông tin tab sản phẩm',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.producttype',
        'example': 'prop(Product type)=="Dịch vụ"',
        'date_created': '2025-01-01 00:00:15',
    },
    'cf8d7be3-f606-4af6-9cf5-c88c796faccb': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product category')),
        'code': 'product_data__general_information__product_category__title',
        'remark': 'Danh mục sản phẩm trong thông tin tab sản phẩm',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.productcategory',
        'example': 'prop(Product category)=="Điện tử"',
        'date_created': '2025-01-01 00:00:15',
    },
    'ab6ef6bc-e836-400e-8a89-57503c21f79c': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product quantity')),
        'code': 'product_quantity',
        'remark': 'Số lượng của một dòng sản phẩm',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:14',
    },
    'f6e535a7-65ef-41ad-93c4-216bb82b87ae': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product unit price')),
        'code': 'product_unit_price',
        'remark': 'Đơn giá của một dòng sản phẩm',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:13',
    },
    '0d573721-bf7c-4281-aea4-60abf26c997e': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Product subtotal')),
        'code': 'product_subtotal_price',
        'remark': 'Thành tiền của một dòng sản phẩm',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:12',
    },
    '374d7846-99e0-4af0-8073-3e048cec8c9d': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Expense type')),
        'code': 'expense_item_data__title',
        'remark': 'Loại chi phí trong thông tin tab chi phí',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.expenseitem',
        'example': 'prop(Expense type)=="Deployment expense"',
        'date_created': '2025-01-01 00:00:11',
    },
    'f67b209c-852a-48d0-8036-e7fdc421f42a': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Labor expense type')),
        'code': 'expense_data__title',
        'remark': 'Loại chi phí nhân công trong thông tin tab chi phí',
        'type': 5,
        'is_sale_indicator': True,
        'content_type': 'saledata.expense',
        'example': 'prop(Labor expense type)=="Deployment manday"',
        'date_created': '2025-01-01 00:00:10',
    },
    '57933f39-3e0e-4754-8205-314573da97fe': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Expense quantity')),
        'code': 'expense_quantity',
        'remark': 'Số lượng của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:09',
    },
    'e4e6d755-4f14-402a-ac2c-d16b1cae7dbd': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Expense unit price')),
        'code': 'expense_price',
        'remark': 'Đơn giá của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:08',
    },
    '09aa4090-762d-4942-9676-24da8340284e': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Expense subtotal before tax')),
        'code': 'expense_subtotal_price',
        'remark': 'Thành tiền của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:07',
    },
    '8b4cdf06-400f-45a7-895f-fcf3886275d7': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Expense subtotal after tax')),
        'code': 'expense_subtotal_price_after_tax',
        'remark': 'Thành tiền sau thuế của một dòng chi phí',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:06',
    },
    '572531de-d9f3-4e2b-8a2e-424a6e832ffa': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total revenue after tax')),
        'code': 'total_product',
        'remark': 'Total revenue of sale order',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:05',
    },
    '1b93c48c-fbbf-460e-8bd6-00df89439c1c': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total cost after tax')),
        'code': 'total_cost',
        'remark': 'Total cost of sale order',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:04',
    },
    'f919ddc7-bcb1-42c0-a84d-01cd48c7e9b4': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total expense after tax')),
        'code': 'total_expense',
        'remark': 'Total expense of sale order',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:03',
    },
    '474ae19c-7dde-4c6d-b9cd-ad6b19af21ce': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total revenue before tax')),
        'code': 'total_product_revenue_before_tax',
        'remark': 'Total revenue before tax of sale order (after discount on total, apply promotion,...)',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:02',
    },
    '3b4cf21c-93fb-4e67-bb02-2eed12ef334f': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total cost before tax')),
        'code': 'total_cost_pretax_amount',
        'remark': 'Total cost before tax of sale order',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:01',
    },
    '9df853f6-522d-45cd-a37f-a8f18f3e496b': {
        'application_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
        'title': str(trans('Total expense before tax')),
        'code': 'total_expense_pretax_amount',
        'remark': 'Total expense before tax of sale order',
        'type': 6,
        'is_sale_indicator': True,
        'date_created': '2025-01-01 00:00:00',
    },
    # PRINT
    **SaleOrder_data__params,
}

AppProp_SaleData_Delivery_data = {
    # 1373e903-909c-4b77-9957-8bcf97e8d6d3 # sales.OrderDelivery
    # General fields
    '3fef3ac1-685f-45a0-ab78-a925945569c9': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Estimated delivery date',
        'code': 'estimated_delivery_date',
        'type': 2,
    },
    '97528d8d-6afb-478b-aca3-c19707e86d0d': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Actual delivery date',
        'code': 'actual_delivery_date',
        'type': 2,
    },
    '90f5c396-9536-48bf-b39c-e5d9c7628163': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Descriptions',
        'code': 'remarks',
        'type': 1,
    },
    '2773759d-6a10-4421-825a-1c9a0391eb84': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Employee inherit',
        'code': 'employee_inherit',
        'type': 5,
    },
    '987f4ff4-9b89-41a7-b05f-3589b9807861': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Attachments',
        'code': 'attachments',
        'remark': 'attachments of delivery',
        'code_related': [
            'employee_inherit_id',
        ],
        'type': 5,
    },
    '5f4d7b52-5805-411f-9d6d-d6f7ce91ff3c': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Shipping address',
        'code': 'shipping_address',
        'type': 1,
    },
    '0cd3a273-cc60-4634-b11d-fb4346f72572': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Billing address',
        'code': 'billing_address',
        'type': 1,
    },
    '0255377b-e1e7-4b96-907e-60f4bb0d0a73': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Product quantity',
        'code': 'ready_quantity',
        'type': 1,
    },
    'f2195dff-0295-40c8-970f-192da0953108': {
        'application_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
        'title': 'Products',
        'code': 'products',
        'remark': 'detail products of delivery',
        'code_related': [
            'employee_inherit_id',
        ],
        'type': 1,
    },
    **Delivery_data__params
}

AppProp_Eoffice_Leave_data = {
    'c5e70a65-362e-4350-9300-f2d2de4676be': {
        'application_id': 'baff033a-c416-47e1-89af-b6653534f06e',
        'title': 'Title',
        'code': 'title',
        'type': 1,
    },
    'e218e34c-80e8-49b5-9fe2-8042c2af65c0': {
        'application_id': 'baff033a-c416-47e1-89af-b6653534f06e',
        'title': 'Date',
        'code': 'request_date',
        'type': 2,
    },
    '172ba1ae-4692-4613-9145-f633b7dfc397': {
        'application_id': 'baff033a-c416-47e1-89af-b6653534f06e',
        'title': 'Beneficiary',
        'code': 'employee_inherit',
        'type': 5,
    },
    '98c92a00-4abd-40f6-b354-e2c9141d36cd': {
        'application_id': 'baff033a-c416-47e1-89af-b6653534f06e',
        'title': 'Detail tab',
        'code': 'detail_data',
        'type': 1,
    },
    '62cba93c-ddcc-4e44-8a20-10cda49276c6': {
        'application_id': 'baff033a-c416-47e1-89af-b6653534f06e',
        'title': 'Total leave of absence',
        'code': 'total',
        'type': 6,
        'is_wf_zone': False,
        'is_wf_condition': True,
    },
}

AppProp_Eoffice_Business_trip_data = {
    '38c2afd8-f4a8-4dac-a709-39e69ba8f9e6': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Title',
        'code': 'title',
        'type': 1,
    },
    '9351e068-8fc9-4431-99ac-66454998aff0': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Departure',
        'code': 'departure',
        'type': 5,
    },
    '77ae7fd2-5982-434b-b4d7-4668ba28fbba': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Destination',
        'code': 'destination',
        'type': 5,
    },
    '99638e9d-2136-4060-84a2-45568b833bec': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Employee on trip',
        'code': 'employee_on_trip',
        'type': 5,
    },
    'de46a5ae-b447-424e-b364-685d0ddaf26d': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Date from',
        'code': 'date_f',
        'type': 2,
    },
    '8323f1d7-7e69-4c24-b8d2-458c9fb2d73e': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Date to',
        'code': 'date_t',
        'type': 2,
    },
    '94bdd32e-177a-4b8e-9491-03749ef9514f': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Time ranges from',
        'code': 'morning_f',
        'type': 4,
    },
    'eb5f70bf-bfe5-412b-93a5-02390ddea5bd': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Time ranges to',
        'code': 'morning_t',
        'type': 4,
    },
    'c6e40f86-b4f0-4670-b336-68ee09efb898': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Attachment file',
        'code': 'attachment',
        'type': 5,
    },
    '6520174d-4fb9-4152-ba12-a853e9cbcf36': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Detail Expense list',
        'code': 'expense_items',
        'type': 1,
    },
    'daa48598-822b-41ae-8437-26f9101d1d54': {
        'application_id': '87ce1662-ca9d-403f-a32e-9553714ebc6d',
        'title': 'Total day',
        'code': 'total_day',
        'type': 6,
    },
}

AppProp_AssetTools_Provide_data = {
    "0ad5bb6a-d55e-4baf-b102-5d7d73884793": {
        "application_id": "55ba3005-6ccc-4807-af27-7cc45e99e3f6",
        "title": "Title",
        "code": "title",
        "type": 1,
    },
    "d3321f9e-99ba-4a6d-99c6-ae64bd983a4e": {
        "application_id": "55ba3005-6ccc-4807-af27-7cc45e99e3f6",
        "title": "Beneficiary",
        "code": "employee_inherit",
        "type": 5,
    },
    "b4e91361-77f4-41c9-bcbf-745b09287c43": {
        "application_id": "55ba3005-6ccc-4807-af27-7cc45e99e3f6",
        "title": "Note",
        "code": "remark",
        "type": 1,
    },
    "023b1786-fdd1-4554-82c3-e78743690cf6": {
        "application_id": "55ba3005-6ccc-4807-af27-7cc45e99e3f6",
        "title": "Tab request",
        "code": "products",
        "type": 5,
    },
    "7afd28ad-8d01-4c0e-9fd2-fbe423cb7cf1": {
        "application_id": "55ba3005-6ccc-4807-af27-7cc45e99e3f6",
        "title": "Tab Attachment",
        "code": "attachments",
        "type": 5,
    }
}

AppProp_AssetTools_Delivery_data = {
    "6569747b-66d6-4e77-b760-5ee4289ef207": {
        "application_id": "41abd4e9-da89-450b-a44a-da1d6f8a5cd2",
        "title": "Title",
        "code": "title",
        "type": 1,
    },
    "1a09a053-72a8-449c-99f5-c7db1b0115af": {
        "application_id": "41abd4e9-da89-450b-a44a-da1d6f8a5cd2",
        "title": "Date Delivery",
        "code": "date_created",
        "type": 5,
    },
    "14132e53-bc2e-4387-a40b-a315a7d29e4a": {
        "application_id": "41abd4e9-da89-450b-a44a-da1d6f8a5cd2",
        "title": "Note",
        "code": "remark",
        "type": 1,
    },
    "a41f4519-498f-415f-94ee-a56e55a0837b": {
        "application_id": "41abd4e9-da89-450b-a44a-da1d6f8a5cd2",
        "title": "Tab delivery",
        "code": "products",
        "type": 5,
    },
    "fff91a0f-f277-42ba-bb17-5edd71c63352": {
        "application_id": "41abd4e9-da89-450b-a44a-da1d6f8a5cd2",
        "title": "Tab Attachment",
        "code": "attachments",
        "type": 5,
    }
}

AppProp_AssetTools_Return_data = {
    "faa260ce-2a44-4270-84c3-6934153817d3": {
        "application_id": "08e41084-4379-4778-9e16-c09401f0a66e",
        "title": "Title",
        "code": "title",
        "type": 1,
    },
    "2809193b-cd88-4fa2-9c27-85c54cdbc022": {
        "application_id": "08e41084-4379-4778-9e16-c09401f0a66e",
        "title": "Date Return",
        "code": "date_return",
        "type": 5,
    },
    "8f8ce65d-b758-4fd1-8359-fcf935f19f0f": {
        "application_id": "08e41084-4379-4778-9e16-c09401f0a66e",
        "title": "Note",
        "code": "remark",
        "type": 1,
    },
    "3ec4ba83-8ae4-457a-9801-82578649f529": {
        "application_id": "08e41084-4379-4778-9e16-c09401f0a66e",
        "title": "Tab return",
        "code": "products",
        "type": 5,
    },
    "28340e18-d2f0-4e36-98ea-9b809eb31ac7": {
        "application_id": "08e41084-4379-4778-9e16-c09401f0a66e",
        "title": "Tab Attachment",
        "code": "attachments",
        "type": 5,
    }
}

AppProp_Sales_Project_data = {
    "44c83ee9-9c32-41b8-990d-549574469feb": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Title",
        "code": "title",
        "type": 1,
    },
    "31149baa-3418-4882-aa8f-c26780daa0c6": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Project PM",
        "code": "project_pm",
        "type": 5,
    },
    "e195f491-f0f2-43ca-914d-6d2cb905f959": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Project PM",
        "code": "employee_inherit",
        "type": 5,
    },
    "df28e122-88f1-45ce-a605-8ea4d11ace01": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Start date",
        "code": "start_date",
        "type": 2,
    },
    "78d897d9-db09-4854-8ee4-2a13dffcdc80": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Finish date",
        "code": "finish_date",
        "type": 2,
    },
    "3d63709c-5af0-4784-8283-8453c88bd4de": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Groups",
        "code": "groups",
        "type": 5,
    },
    "fcb61229-bb62-44d0-a4ba-6b13e1eacee9": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Works",
        "code": "works",
        "type": 5,
    },
    "dfbd2db4-9438-4629-baf4-711a9c0bc134": {
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
        "title": "Members",
        "code": "members",
        "type": 5,
    }
}

AppProp_Sales_Project_Baseline_data = {}

# haind
AppProp_SaleData_Advance_Payment_data = {
    "2142ad51-81b7-48a0-a073-58f516c40c88": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Opportunity",
        "code": "opportunity_id",
        "type": 5,
        "content_type": 'opportunity.Opportunity',
        'is_wf_zone': True,
    },
    "98a42060-1018-476d-965a-1158089072f6": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Employee inherit",
        "code": "employee_inherit_id",
        "type": 5,
        "content_type": 'hr.Employee',
        'is_wf_zone': True,
    },
    "5ef3c139-ec40-4e03-bcfa-e631baaa5e73": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
    "43206581-8152-4e02-b34a-011d3651434a": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Date created",
        "code": "date_created",
        "type": 1,
        'is_wf_zone': True,
    },
    "1b379df0-49b6-40de-a11b-dfb7a8575da2": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Employee created",
        "code": "employee_created_id",
        "type": 5,
        "content_type": 'hr.Employee',
        'is_wf_zone': True,
    },
    "2192a1b9-679d-48d6-881a-f85553868b42": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Quotation",
        "code": "quotation_id",
        "type": 5,
        "content_type": 'quotation.Quotation',
        'is_wf_zone': True,
    },
    "c3613c55-43b7-4d0b-97c4-389e8716a470": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Sale order",
        "code": "sale_order_id",
        "type": 5,
        "content_type": 'saleorder.SaleOrder',
        'is_wf_zone': True,
    },
    "ceba8e0a-1613-4903-bccd-d6895b236abf": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Advance payment type",
        "code": "advance_payment_type",
        "type": 6,
        'is_wf_zone': True,
    },
    "89c57dd4-2e8d-47f3-b1ee-f7cb299448b7": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Supplier",
        "code": "supplier_id",
        'type': 5,
        'content_type': 'saledata.Account',
        'is_wf_zone': True,
    },
    "3dca605f-1a45-454c-9909-973904fcd820": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Advance payment method",
        "code": "method",
        "type": 6,
        'is_wf_zone': True,
    },
    "95f1ca37-0277-4ab9-9205-bcc4637e3431": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Return date",
        "code": "return_date",
        "type": 2,
        'is_wf_zone': True,
    },
    "72848cc3-54b5-44d9-9deb-6c503cd64d04": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Money gave/received",
        "code": "money_gave",
        "type": 1,
        'is_wf_zone': True,
    },
    # tab line detail
    "51840528-2a9f-448b-afcb-ad0f421fd523": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Line detail Tab",
        "code": "ap_item_list",
        "type": 1,
        'is_wf_zone': True,
    },
    # tab plan
    "ff3ba757-cd27-4b8c-8b4c-7405401b528c": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "Plan Tab",
        "code": "plan_tab",
        "type": 1,
        'is_wf_zone': True,
    },
    # tab file
    "64580a12-f841-4e1b-82ac-73b8506f28ef": {
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",
        "title": "File Tab",
        "code": "attachment",
        "type": 1,
        'is_wf_zone': True,
    },
    # workflow
    '10e6397d-cd03-4d1f-8bc6-18df5ca1e0ab': {
        'application_id': '57725469-8b04-428a-a4b0-578091d0e4f5',
        'title': 'Advance value',
        'code': 'advance_value',
        'type': 6,
        'is_wf_condition': True,
        'is_wf_zone': True,
    },
    **AdvancePayment_data__params
}

AppProp_SaleData_AP_Invoice_data = {
    "2308d013-d7a8-4f45-8f9d-8dc579833a5a": {
        "application_id": "c05a6cf4efff47e0afcf072017b8141a",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_AR_Invoice_data = {
    "813ecad6-989a-4e70-88d1-2b66efa3c650": {
        "application_id": "1d7291dd1e59491783a31cc07cfc4638",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_Goods_Issue_data = {
    "66cd789a-eb63-4ff0-a14d-68da90f33c7b": {
        "application_id": "f26d7ce4e990420a8ec62dc307467f2c",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_Goods_Return_data = {
    **Goods_Return_data__params
}

AppProp_SaleData_Goods_Transfer_data = {
    **Goods_Transfer_data__params
}

AppProp_SaleData_IA_data = {
    **IA_data__params
}

AppProp_SaleData_Payment_data = {
    "5bf7bb8f-f0de-42d3-a95a-4643d63746c0": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Opportunity",
        "code": "opportunity_id",
        "type": 5,
        "content_type": 'opportunity.Opportunity',
        'is_wf_zone': True,
    },
    "41511943-3112-4ef3-91ca-55123a9015cd": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Employee inherit",
        "code": "employee_inherit_id",
        "type": 5,
        "content_type": 'hr.Employee',
        'is_wf_zone': True,
    },
    "6c8894ba-c3c6-404f-939c-22ccce4c0cbd": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
    "c9e120be-5a23-43db-ac36-9ddacbaa41ec": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Date created",
        "code": "date_created",
        "type": 1,
        'is_wf_zone': True,
    },
    "21399374-a08e-4ba9-a40f-170866fa64ee": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Employee created",
        "code": "employee_created_id",
        "type": 5,
        "content_type": 'hr.Employee',
        'is_wf_zone': True,
    },
    "6c892c95-8bd5-4f09-a9be-92963b72ac29": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Quotation",
        "code": "quotation_id",
        "type": 5,
        "content_type": 'quotation.Quotation',
        'is_wf_zone': True,
    },
    "c576f290-1ba7-48f6-95ee-decbd8a54079": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Sale order",
        "code": "sale_order_id",
        "type": 5,
        "content_type": 'saleorder.SaleOrder',
        'is_wf_zone': True,
    },
    "85556007-ef17-427d-ac7e-c65c4b10c210": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Internal payment",
        "code": "is_internal_payment",
        'type': 4,
        'is_wf_zone': True,
    },
    "67099494-859c-4ad9-adad-92175230d08f": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Employee payment",
        "code": "employee_payment_id",
        'type': 5,
        'content_type': 'hr.Employee',
        'is_wf_zone': True,
    },
    "5ce2a8b3-72da-4c7e-a5f1-ab8982801a8b": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Supplier",
        "code": "supplier_id",
        'type': 5,
        'content_type': 'saledata.Account',
        'is_wf_zone': True,
    },
    "3811bd07-bab6-452e-89a4-6352c2c667d3": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Payment method",
        "code": "method",
        "type": 6,
        'is_wf_zone': True,
    },
    # tab line detail
    "09b7660e-adde-4515-bcf1-764020f71e71": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Tab detail",
        "code": "payment_expense_valid_list",
        "type": 1,
        'is_wf_zone': True,
    },
    # tab plan
    "20183aa0-49b4-4918-9a8c-ea6790afa52d": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "Plan Tab",
        "code": "plan_tab",
        "type": 1,
        'is_wf_zone': True,
    },
    # tab file
    "f292552c-7dd6-47fd-8ca0-457ce117dfe3": {
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
        "title": "File Tab",
        "code": "attachment",
        "type": 1,
        'is_wf_zone': True,
    },
    # workflow
    '8f89a3f6-e8ba-48df-845f-cc6d82dbfbaa': {
        'application_id': '1010563f-7c94-42f9-ba99-63d5d26a1aca',
        'title': 'Payment value',
        'code': 'payment_value',
        'type': 6,
        'is_wf_condition': True,
        'is_wf_zone': True,
    },
    **Payment_data__params
}

AppProp_SaleData_Purchase_Quotation_data = {
    "4cce8c82-fd38-4e07-8ccc-4d15dea27d09": {
        "application_id": "f52a966a2eb24851852deff61efeb896",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_Purchase_Quotation_Request_data = {
    "62251ec1-9daa-4992-a8ea-43bb5b2803eb": {
        "application_id": "d78bd5f38a8d48a3ad62b50d576ce173",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_Purchase_Request_data = {
    "89cbbeca-c419-479d-bc25-7cfd71bc597c": {
        "application_id": "fbff9b3ff7c9414f995996d3ec2fb8bf",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_Return_Payment_data = {
    "192965a3-95ca-47a7-9247-58e1cbf652d4": {
        "application_id": "65d36757-557e-4534-87ea-5579709457d7",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
    "c5c05715-bf9d-4c08-9b6b-4cfa649bf806": {
        "application_id": "65d36757-557e-4534-87ea-5579709457d7",
        "title": "Return payment method",
        "code": "method",
        "type": 6,
        'is_wf_zone': True,
    },
    # tab line detail
    "6ae7e6cc-d3ff-417f-8407-eee143078889": {
        "application_id": "65d36757-557e-4534-87ea-5579709457d7",
        "title": "Tab detail",
        "code": "cost",
        "type": 1,
        'is_wf_zone': True,
    },
    "0db6a091-3f1a-4948-bcc9-716287ab9427": {
        "application_id": "65d36757-557e-4534-87ea-5579709457d7",
        "title": "Money received",
        "code": "money_received",
        "type": 3,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_Distribution_Plan_data = {
    "62e2a55d-1054-44f1-9f30-db0829e6973d": {
        "application_id": "57a32d5a-3580-43b7-bf31-953a1afc68f4",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_BOM_data = {
    "216b4c85-3793-4425-84fb-64f0b6102661": {
        "application_id": "2de9fb91-4fb9-48c8-b54e-c03bd12f952b",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_FinancialCashflow_CashInflow_data = {
    "355c278c-7901-4f6d-8330-76eb9082b40f": {
        "application_id": "7ba35923-d8ff-4f6d-bf80-468a7190a63b",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_FinancialRecon_Recon_data = {
    "355c278c-7901-4f6d-8330-76eb9082b40f": {
        "application_id": "b690b9ff-670a-474b-8ae2-2c17d7c30f40",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
}
####

AppProp_SaleData_Contract_Approval_data = {
    # 58385bcf-f06c-474e-a372-cadc8ea30ecc # contract.ContractApproval
    '8c5568f7-3bde-4461-b6f0-73c53e645e5d': {
        'application_id': '58385bcf-f06c-474e-a372-cadc8ea30ecc',
        'title': 'Title',
        'code': 'title',
        'type': 1,
        'is_print': True,
        'is_wf_zone': True,
    },
    '9820a32b-50b1-435a-bd41-bc548c2535a7': {
        'application_id': '58385bcf-f06c-474e-a372-cadc8ea30ecc',
        'title': 'Abstract review',
        'code': 'abstract_content',
        'type': 1,
        'is_wf_zone': True,
    },
    '6dbb5d48-69d7-4b8e-a329-d7dd86ab1349': {
        'application_id': '58385bcf-f06c-474e-a372-cadc8ea30ecc',
        'title': 'Trade review',
        'code': 'trade_content',
        'type': 1,
        'is_wf_zone': True,
    },
    'f809300c-4c3a-4453-8c15-18a56caa8973': {
        'application_id': '58385bcf-f06c-474e-a372-cadc8ea30ecc',
        'title': 'Legal review',
        'code': 'legal_content',
        'type': 1,
        'is_wf_zone': True,
    },
    'd63c108d-8655-4e86-89cf-00aff26a2202': {
        'application_id': '58385bcf-f06c-474e-a372-cadc8ea30ecc',
        'title': 'Payment review',
        'code': 'payment_content',
        'type': 1,
        'is_wf_zone': True,
    },
}

AppProp_SaleData_Bidding_data = {
    "b8ad6020-c87d-4020-b72c-8a0cde3f4502": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Opportunity",
        "code": "opportunity",
        "type": 5,
        "content_type": "opportunity.opportunity",
        'is_wf_zone': True,
    },
    "36f85840-f8a0-41a3-bd8a-6d958d25d6c1": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Employee Inherit",
        "code": "employee_inherit_id",
        "type": 5,
        'content_type': 'hr.employee',
        'is_wf_zone': True,
    },
    "5ef3c139-ec40-4e03-bcfa-e631baaa5e73": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
    "9ae1da51-3a1a-464e-92f5-c6ca271909f4": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Bid value",
        "code": "bid_value",
        "type": 6,
        'is_wf_zone': True,
    },
    "e426222a-abce-41bc-9c3d-5216e8bf4888": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Bid bond value",
        "code": "bid_bond_value",
        "type": 6,
        'is_wf_zone': True,
    },
    "d76baec5-3a79-4fdc-95b0-6abdcdea2e2a": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Bid date",
        "code": "bid_date",
        "type": 2,
        'is_wf_zone': True,
    },
    "df37d7b1-c94b-4586-ae6b-6eeec518d61d": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Venture Partner",
        "code": "venture_partner",
        "type": 1,
        'is_wf_zone': True,
    },
    "1def7e01-7adf-485b-b63e-adbebebada68": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Document Data",
        "code": "document_data",
        "type": 1,
        'is_wf_zone': True,
    },
    "40ea2cdd-a173-4e8a-9bc3-1b6b8fc7ecc2": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Attachment",
        "code": "attachment",
        "type": 1,
        'is_wf_zone': True,
    },
    "5c15c1cc-2a85-4c02-a57e-ea7272f48243": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Security Type",
        "code": "security_type",
        "type": 6,
        'is_wf_zone': True,
    },
    "0ef463d5-a722-44e8-9d72-80e52e10feb0": {
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
        "title": "Tinymce Content",
        "code": "tinymce_content",
        "type": 1,
        'is_wf_zone': True,
    },
    **Bidding_data__params
}

AppProp_SaleData_Consulting_data = {
    "21b8f9c1-0cba-42b4-bde4-5cadecd661f4": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Opportunity",
        "code": "opportunity",
        "type": 5,
        "content_type": "opportunity.opportunity",
        'is_wf_zone': True,
    },
    "7067a027-4a9e-4396-b81b-f201df7abcff": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Employee Inherit",
        "code": "employee_inherit",
        "type": 5,
        'content_type': 'hr.employee',
        'is_wf_zone': True,
    },
    "e8295df3-5e01-4a3d-bb9e-a5e771926ab5": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Customer",
        "code": "customer",
        "type": 5,
        'content_type': 'saledata.account',
        'is_wf_zone': True,
        'is_wf_condition': True
    },
    "899ff0a5-bf03-4d49-b5c4-f1efb0ae6154": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Title",
        "code": "title",
        "type": 1,
        'is_wf_zone': True,
    },
    "dabe29fe-322e-4580-b3d8-5195cc7642e2": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Consulting value",
        "code": "value",
        "type": 6,
        'is_wf_zone': True,
        'is_wf_condition': True,
    },
    "61560bcf-5915-49ad-9f99-4f10536f54c6": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Consulting date",
        "code": "due_date",
        "type": 2,
        'is_wf_zone': True,
    },
    "afc9f079-3b09-4a0b-a67c-705abe11f6d1": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Product Categories",
        "code": "product_categories",
        "type": 1,
        'is_wf_zone': True,
    },
    "eda3e7ab-4fc6-4cac-a291-dfb63754625c": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Document Data",
        "code": "document_data",
        "type": 1,
        'is_wf_zone': True,
    },
    "3d57b69a-d826-4e0c-a112-806bd7671645": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Attachment",
        "code": "attachment",
        "type": 1,
        'is_wf_zone': True,
    },
    "30693a4b-b7d8-4754-9d73-6bd048e5a914": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Abstract Content",
        "code": "abstract_content",
        "type": 1,
        'is_wf_zone': True,
    },
    "ccd3658e-c210-45ae-8283-3fabe11e9880": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Category in Product Categories",
        "code": "product_categories__product_category",
        "type": 5,
        'content_type': 'saledata.productcategory',
        'is_wf_zone': True,
        "is_wf_condition": True,
    },
    "9c8d217f-45b3-441a-965b-b99203b722db": {
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
        "title": "Total number of Product Categories",
        "code": "product_categories_total_number",
        "type": 6,
        'is_wf_zone': True,
        "is_wf_condition": True,
    },
}

AppProp_SaleData_ReportRevenue_data = {
    "67f15b55-523c-4d2e-a560-26dfca19b50f": {
        "application_id": "c3260940-21ff-4929-94fe-43bc4199d38b",
        "title": "Customer",
        "code": "customer",
        "type": 5,
        "content_type": "saledata.account",
        'is_filter_condition': True,
    },
    "4a6eeecf-758b-4b37-bb71-e87e18cee451": {
        "application_id": "c3260940-21ff-4929-94fe-43bc4199d38b",
        "title": "Customer Name",
        "code": "customer__name",
        "type": 1,
        'is_filter_condition': True,
    },
    "8725286d-86a2-490a-ab3b-071b7e5d9dca": {
        "application_id": "c3260940-21ff-4929-94fe-43bc4199d38b",
        "title": "Revenue",
        "code": "revenue",
        "type": 6,
        'is_filter_condition': True,
    },
    "eaeff00e-e58d-4849-86c8-293b71e7bedd": {
        "application_id": "c3260940-21ff-4929-94fe-43bc4199d38b",
        "title": "Gross Margin (in percent, e.g, 15, 30)",
        "code": "gross_margin",
        "type": 6,
        'is_filter_condition': True,
    },
    "1715395b-0679-4442-8c6d-046bbe86e391": {
        "application_id": "c3260940-21ff-4929-94fe-43bc4199d38b",
        "title": "Gross Profit",
        "code": "gross_profit",
        "type": 6,
        'is_filter_condition': True,
    },
    "1fd330e4-5cb6-43b6-97f8-553486f9e3eb": {
        "application_id": "c3260940-21ff-4929-94fe-43bc4199d38b",
        "title": "Net Income",
        "code": "net_income",
        "type": 6,
        'is_filter_condition': True,
    },
}

ApplicationProperty_data = {
    **Bastion_data_params,
    **AppProp_SaleData_Contact_data,
    **AppProp_SaleData_Account_data,
    **AppProp_SaleData_Quotation_data,
    **AppProp_SaleData_Opportunity_data,
    **AppProp_SaleData_SaleOrder_data,
    **AppProp_Eoffice_Leave_data,
    **AppProp_Eoffice_Business_trip_data,
    **AppProp_AssetTools_Provide_data,
    **AppProp_AssetTools_Delivery_data,
    **AppProp_AssetTools_Return_data,
    **AppProp_Sales_Project_data,
    **AppProp_Sales_Project_Baseline_data,
    **AppProp_SaleData_Delivery_data,
    **AppProp_SaleData_Contract_Approval_data,
    # haind
    **AppProp_SaleData_Advance_Payment_data,
    **AppProp_SaleData_AP_Invoice_data,
    **AppProp_SaleData_AR_Invoice_data,
    **AppProp_SaleData_Goods_Issue_data,
    **AppProp_SaleData_Goods_Return_data,
    **AppProp_SaleData_Goods_Transfer_data,
    **AppProp_SaleData_Payment_data,
    **AppProp_SaleData_Purchase_Quotation_data,
    **AppProp_SaleData_Purchase_Quotation_Request_data,
    **AppProp_SaleData_Purchase_Request_data,
    **AppProp_SaleData_Return_Payment_data,
    **AppProp_SaleData_Distribution_Plan_data,
    **AppProp_SaleData_BOM_data,
    **AppProp_SaleData_FinancialCashflow_CashInflow_data,
    **AppProp_SaleData_FinancialRecon_Recon_data,

    **AppProp_SaleData_Bidding_data,
    **AppProp_SaleData_IA_data,
    **AppProp_SaleData_Consulting_data,
    **AppProp_SaleData_ReportRevenue_data
}
