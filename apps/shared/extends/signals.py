import logging
from copy import deepcopy
from datetime import date, timedelta
from uuid import uuid4

from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save
from django.dispatch import receiver
from django.utils import translation, timezone
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import TaskResult

from apps.core.attachments.models import Files
from apps.core.hr.models import Role, Employee, RoleHolder, EmployeePermission, RolePermission
from apps.core.hr.tasks import sync_plan_app_employee, uninstall_plan_app_employee
from apps.core.log.models import Notifications
from apps.core.process.models import SaleFunction, Process
from apps.core.workflow.models import RuntimeAssignee, WorkflowConfigOfApp, Workflow
from apps.core.workflow.models.runtime import RuntimeViewer, Runtime
from apps.eoffice.leave.models import LeaveConfig, LeaveType, WorkingCalendarConfig, LeaveAvailable
from apps.sales.opportunity.models import (
    OpportunityConfig, OpportunityConfigStage, StageCondition,
    OpportunitySaleTeamMember,
)
from apps.sales.purchasing.models import PurchaseRequestConfig
from apps.sales.quotation.models import (
    QuotationAppConfig, ConfigShortSale, ConfigLongSale, QuotationIndicatorConfig, SQIndicatorDefaultData,
)
from apps.core.base.models import Currency as BaseCurrency, Application, PlanApplication
from apps.core.company.models import Company, CompanyConfig, CompanyFunctionNumber
from apps.masterdata.saledata.models import (
    AccountType, ProductType, TaxCategory, Currency, Price, UnitOfMeasureGroup,
)
from apps.sales.delivery.models import DeliveryConfig
from apps.sales.saleorder.models import (
    SaleOrderAppConfig, ConfigOrderLongSale, ConfigOrderShortSale,
    SaleOrderIndicatorConfig, ORIndicatorDefaultData,
)
from apps.sales.task.models import OpportunityTaskConfig, OpportunityTaskStatus

from .caching import Caching
from .push_notify import TeleBotPushNotify
from .tasks import call_task_background
from ..media_cloud_apis import MediaForceAPI
from ...core.tenant.models import TenantPlan, Tenant
from ...eoffice.assettools.models import AssetToolsConfig
from ...eoffice.businesstrip.models import BusinessRequest, ExpenseItemMapBusinessRequest
from ...eoffice.businesstrip.serializers import BusinessRequestUpdateSerializer

logger = logging.getLogger(__name__)

__all__ = [
    'SaleDefaultData',
    'ConfigDefaultData',
    'update_stock',
]


class SaleDefaultData:
    ProductType_data = [
        {'title': 'Sản phẩm', 'is_default': 1},
        {'title': 'Bán thành phẩm', 'is_default': 1},
        {'title': 'Nguyên vật liệu', 'is_default': 1},
        {'title': 'Dịch vụ', 'is_default': 1},
    ]
    TaxCategory_data = [
        {'title': 'Thuế GTGT', 'is_default': 1},
        {'title': 'Thuế xuất khẩu', 'is_default': 1},
        {'title': 'Thuế nhập khẩu', 'is_default': 1},
        {'title': 'Thuế tiêu thụ đặc biệt', 'is_default': 1},
        {'title': 'Thuế nhà thầu', 'is_default': 1},
    ]
    Currency_data = [
        {'title': 'VIETNAM DONG', 'abbreviation': 'VND', 'is_default': 1, 'is_primary': 1, 'rate': 1.0},
        {'title': 'US DOLLAR', 'abbreviation': 'USD', 'is_default': 1, 'is_primary': 0, 'rate': None},
        {'title': 'YEN', 'abbreviation': 'JPY', 'is_default': 1, 'is_primary': 0, 'rate': None},
        {'title': 'EURO', 'abbreviation': 'EUR', 'is_default': 1, 'is_primary': 0, 'rate': None},
    ]
    Price_general_data = [
        {'title': 'General Price List', 'price_list_type': 0, 'factor': 1.0, 'is_default': 1}
    ]
    Account_types_data = [
        {'title': 'Customer', 'code': 'AT001', 'is_default': 1, 'account_type_order': 0},
        {'title': 'Supplier', 'code': 'AT002', 'is_default': 1, 'account_type_order': 1},
        {'title': 'Partner', 'code': 'AT003', 'is_default': 1, 'account_type_order': 2},
        {'title': 'Competitor', 'code': 'AT004', 'is_default': 1, 'account_type_order': 3}
    ]
    UoM_Group_data = [
        {'title': 'Labor', 'is_default': 1},
    ]
    CompanyFunctionNumber_data = [
        {
            'numbering_by': 0,
            'schema': None,
            'schema_text': None,
            'first_number': None,
            'last_number': None,
            'reset_frequency': None
        }
    ]

    def __init__(self, company_obj):
        self.company_obj = company_obj

    def __call__(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.create_product_type()
                self.create_tax_category()
                self.create_currency()
                self.create_price_default()
                self.create_account_types()
                self.create_uom_group()
                self.create_company_function_number()
            return True
        except Exception as err:
            logger.error(
                '[ERROR][SaleDefaultData]: Company ID=%s, Error=%s',
                str(self.company_obj.id), str(err)
            )
        return False

    def create_product_type(self):
        objs = [
            ProductType(tenant=self.company_obj.tenant, company=self.company_obj, **pt_item)
            for pt_item in self.ProductType_data
        ]
        ProductType.objects.bulk_create(objs)
        return True

    def create_account_types(self):
        objs = [
            AccountType(tenant=self.company_obj.tenant, company=self.company_obj, **at_item)
            for at_item in self.Account_types_data
        ]
        AccountType.objects.bulk_create(objs)
        return True

    def create_tax_category(self):
        objs = [
            TaxCategory(tenant=self.company_obj.tenant, company=self.company_obj, **tc_item)
            for tc_item in self.TaxCategory_data
        ]
        TaxCategory.objects.bulk_create(objs)
        return True

    def create_currency(self):
        currency_list = ['VND', 'USD', 'EUR', 'JPY']
        data_currency = BaseCurrency.objects.filter(code__in=currency_list)
        if data_currency.count() > 0:
            bulk_info = []
            for item in data_currency:
                primary = False
                rate = None
                if item.code == 'VND':
                    primary = True
                    rate = 1.0
                bulk_info.append(
                    Currency(
                        tenant=self.company_obj.tenant,
                        company=self.company_obj,
                        title=item.title,
                        abbreviation=item.code,
                        currency=item,
                        rate=rate,
                        is_primary=primary
                    )
                )
            if len(bulk_info) > 0:
                Currency.objects.bulk_create(bulk_info)
            return True
        return False

    def create_price_default(self):
        primary_current = Currency.objects.filter(
            company=self.company_obj,
            is_primary=True
        ).first()
        if primary_current:
            primary_current_id = str(primary_current.id)
            objs = [
                Price(
                    tenant=self.company_obj.tenant, company=self.company_obj, currency=[primary_current_id],
                    **p_item
                )
                for p_item in self.Price_general_data
            ]
            Price.objects.bulk_create(objs)
            return True
        return False

    def create_uom_group(self):
        objs = [
            UnitOfMeasureGroup(tenant=self.company_obj.tenant, company=self.company_obj, **uom_group_item)
            for uom_group_item in self.UoM_Group_data
        ]
        UnitOfMeasureGroup.objects.bulk_create(objs)
        return True

    def create_company_function_number(self):
        objs = []
        for function_index in range(10):
            for cf_item in self.CompanyFunctionNumber_data:
                objs.append(
                    CompanyFunctionNumber(
                        company=self.company_obj,
                        function=function_index,
                        **cf_item
                    )
                )
        CompanyFunctionNumber.objects.bulk_create(objs)
        return True


class ConfigDefaultData:
    """
    Class support create all config of company when signal new Company just created
    """
    opportunity_config_stage_data = [
        {
            'indicator': 'Qualification',
            'description': 'Giai đoạn thẩm định thông tin cơ hội kinh doanh',
            'win_rate': 10,
            'is_default': True,
            'logical_operator': 0,
            'is_deal_closed': False,
            'is_delivery': False,
            'is_closed_lost': False,
            'is_delete': False,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'e4e0c770-a0d1-492d-beae-3b31dcb391e1',
                        'title': 'Customer'
                    },  # id application property Customer
                    'comparison_operator': '≠',
                    'compare_data': 0,
                }
            ]
        },
        {
            'indicator': 'Needs Analysis',
            'description': 'Giai đoạn phân tích, khảo sát các yêu cầu của khách hàng',
            'win_rate': 20,
            'is_default': True,
            'logical_operator': 0,
            'is_deal_closed': False,
            'is_delivery': False,
            'is_closed_lost': False,
            'is_delete': True,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'e4e0c770-a0d1-492d-beae-3b31dcb391e1',
                        'title': 'Customer'
                    },  # application property Customer
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': '496aca60-bf3d-4879-a4cb-6eb1ebaf4ce8',
                        'title': 'Product Category'
                    },  # application property Product Category
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': '43009b1a-a25d-43be-ab97-47540a2f00cb',
                        'title': 'Close Date'
                    },  # application property Close Date
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
            ]
        },
        {
            'indicator': 'Proposal',
            'description': 'Giai đoạn gửi đề xuất sản phẩm dịch vụ cho khách hàng',
            'win_rate': 50,
            'is_default': True,
            'logical_operator': 0,
            'is_deal_closed': False,
            'is_delivery': False,
            'is_closed_lost': False,
            'is_delete': True,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'e4e0c770-a0d1-492d-beae-3b31dcb391e1',
                        'title': 'Customer'
                    },  # application property Customer
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': '496aca60-bf3d-4879-a4cb-6eb1ebaf4ce8',
                        'title': 'Product Category'
                    },  # application property Product Category
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': '43009b1a-a25d-43be-ab97-47540a2f00cb',
                        'title': 'Close Date'
                    },  # application property Close Date
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': '35dbf6f2-78a8-4286-8cf3-b95de5c78873',
                        'title': 'Decision maker'
                    },  # application property Decision maker
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': '39b50254-e32d-473b-8380-f3b7765af434',
                        'title': 'Product.Line.Detail'
                    },  # application property Product.Line.Detail
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
            ]
        },
        {
            'indicator': 'Negotiation',
            'description': 'Giai đoạn thương lượng giá, phạm vi cv, hợp đồng, các điều kiện thương mại...',
            'win_rate': 80,
            'is_default': True,
            'logical_operator': 0,
            'is_deal_closed': False,
            'is_delivery': False,
            'is_closed_lost': False,
            'is_delete': True,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'acab2c1e-74f2-421b-8838-7aa55c217f72',
                        'title': 'Quotation.confirm'
                    },  # application property Quotation.confirm
                    'comparison_operator': '=',
                    'compare_data': 0,
                },

            ]
        },
        {
            'indicator': 'Closed Won',
            'description': 'Đóng thành công cơ hội, khách hàng xác nhận mua hàng, ký hợp dồng..',
            'win_rate': 100,
            'is_default': True,
            'logical_operator': 0,
            'is_deal_closed': False,
            'is_delivery': False,
            'is_closed_lost': False,
            'is_delete': False,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': '9db4e835-c647-4de5-aa1c-43304ddeccd1',
                        'title': 'SaleOlder.status'
                    },  # application property SaleOlder.status
                    'comparison_operator': '=',
                    'compare_data': 0,
                },
            ]
        },
        {
            'indicator': 'Closed Lost',
            'description': 'Cơ hội thất bại',
            'win_rate': 0,
            'is_default': True,
            'logical_operator': 1,
            'is_deal_closed': False,
            'is_delivery': False,
            'is_closed_lost': True,
            'is_delete': False,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': '92c8035a-5372-41c1-9a8e-4b048d8af406',
                        'title': 'Lost By Other Reason'
                    },  # application property Lost By Other Reason

                    'comparison_operator': '=',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': 'c8fa79ae-2490-4286-af25-3407e129fedb',
                        'title': 'Competitor.Win'
                    },  # application property Competitor.Win
                    'comparison_operator': '=',
                    'compare_data': 0,
                },
            ]
        },
        {
            'indicator': 'Delivery',
            'description': 'Đang giao hàng/triển khai',
            'win_rate': 100,
            'is_default': True,
            'logical_operator': 0,
            'is_deal_closed': False,
            'is_delivery': True,
            'is_closed_lost': False,
            'is_delete': True,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'b5aa8550-7fc5-4cb8-a952-b6904b2599e5',
                        'title': 'SaleOrder.Delivery.Status'
                    },  # application property SaleOrder.Delivery.Status
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
            ]
        },
        {
            'indicator': 'Deal Close',
            'description': 'Kết thúc bán hàng/Dự án',
            'win_rate': 0,
            'is_default': True,
            'logical_operator': 0,
            'is_deal_closed': True,
            'is_delivery': False,
            'is_closed_lost': False,
            'is_delete': False,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'f436053d-f15a-4505-b368-9ccdf5afb5f6',
                        'title': 'Close Deal'
                    },  # application property Close Deal
                    'comparison_operator': '=',
                    'compare_data': 0,
                },
            ]
        }
    ]

    function_process_data = [
        {
            'function_id': 'e66cfb5a-b3ce-4694-a4da-47618f53de4c',
            'is_free': True,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': '14dbc606-1453-4023-a2cf-35b1cd9e3efd',
            'is_free': True,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': 'dec012bf-b931-48ba-a746-38b7fd7ca73b',
            'is_free': True,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': '2fe959e3-9628-4f47-96a1-a2ef03e867e3',
            'is_free': True,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': '319356b4-f16c-4ba4-bdcb-e1b0c2a2c124',
            'is_free': False,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': 'b9650500-aba7-44e3-b6e0-2542622702a3',
            'is_free': False,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': 'a870e392-9ad2-4fe2-9baa-298a38691cf2',
            'is_free': False,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': '31c9c5b0-717d-4134-b3d0-cc4ca174b168',
            'is_free': False,
            'is_in_process': True,
            'is_default': True,
        },
        {
            'function_id': '1373e903-909c-4b77-9957-8bcf97e8d6d3',
            'is_free': True,
            'is_in_process': False,
            'is_default': True,
        },
        {
            'function_id': '57725469-8b04-428a-a4b0-578091d0e4f5',
            'is_free': True,
            'is_in_process': False,
            'is_default': True,
        },
        {
            'function_id': '1010563f-7c94-42f9-ba99-63d5d26a1aca',
            'is_free': True,
            'is_in_process': False,
            'is_default': True,
        },
        {
            'function_id': '65d36757-557e-4534-87ea-5579709457d7',
            'is_free': True,
            'is_in_process': False,
            'is_default': True,
        }
    ]

    def __init__(self, company_obj):
        self.company_obj = company_obj

    def company_config(self):
        obj, _created = CompanyConfig.objects.get_or_create(
            company=self.company_obj,
            defaults={
                'language': 'vi',
                'currency': BaseCurrency.objects.get(code='VND'),
            },
        )
        return obj

    def delivery_config(self):
        DeliveryConfig.objects.get_or_create(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            defaults={
                'is_picking': False,
                'is_partial_ship': True,
            },
        )

    def quotation_config(self):
        short_sale_config = {
            'is_choose_price_list': False,
            'is_input_price': False,
            'is_discount_on_product': False,
            'is_discount_on_total': False
        }
        long_sale_config = {
            'is_not_input_price': False,
            'is_not_discount_on_product': False,
            'is_not_discount_on_total': False,
        }
        config, created = QuotationAppConfig.objects.get_or_create(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            defaults={
                'short_sale_config': short_sale_config,
                'long_sale_config': long_sale_config,
            },
        )
        if created:
            ConfigShortSale.objects.create(
                quotation_config=config,
                **short_sale_config
            )
            ConfigLongSale.objects.create(
                quotation_config=config,
                **long_sale_config
            )

    def sale_order_config(self):
        short_sale_config = {
            'is_choose_price_list': False,
            'is_input_price': False,
            'is_discount_on_product': False,
            'is_discount_on_total': False
        }
        long_sale_config = {
            'is_not_input_price': False,
            'is_not_discount_on_product': False,
            'is_not_discount_on_total': False,
        }
        config, created = SaleOrderAppConfig.objects.get_or_create(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            defaults={
                'short_sale_config': short_sale_config,
                'long_sale_config': long_sale_config,
            },
        )
        if created:
            ConfigOrderShortSale.objects.create(
                sale_order_config=config,
                **short_sale_config
            )
            ConfigOrderLongSale.objects.create(
                sale_order_config=config,
                **long_sale_config
            )

    def opportunity_config(self):
        OpportunityConfig.objects.get_or_create(
            company=self.company_obj,
            defaults={
                'is_select_stage': False,
                'is_input_win_rate': False,
            },
        )

    def opportunity_config_stage(self):
        for stage in self.opportunity_config_stage_data:
            config_stage = OpportunityConfigStage.objects.create(
                company=self.company_obj,
                **stage
            )
            for condition in stage['condition_datas']:
                StageCondition.objects.create(
                    stage=config_stage,
                    condition_property_id=condition['condition_property']['id'],
                    comparison_operator=condition['comparison_operator'],
                    compare_data=condition['compare_data']
                )

    def quotation_indicator_config(self):
        bulk_info = []
        for data in SQIndicatorDefaultData.INDICATOR_DATA:
            bulk_info.append(
                QuotationIndicatorConfig(
                    tenant=self.company_obj.tenant,
                    company=self.company_obj,
                    **data,
                )
            )
        QuotationIndicatorConfig.objects.bulk_create(bulk_info)

    def sale_order_indicator_config(self):
        bulk_info = []
        for data in ORIndicatorDefaultData.INDICATOR_DATA:
            bulk_info.append(
                SaleOrderIndicatorConfig(
                    tenant=self.company_obj.tenant,
                    company=self.company_obj,
                    **data,
                )
            )
        SaleOrderIndicatorConfig.objects.bulk_create(bulk_info)

    def task_config(self):
        # create config default for company
        config, created = OpportunityTaskConfig.objects.get_or_create(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            defaults={
                'list_status': [
                    {
                        'name': 'To do', 'translate_name': 'Việc cần làm', 'order': 1, 'is_edit': False, 'task_kind': 1,
                        'task_color': '#abe3e5'
                    },
                    {
                        'name': 'In Progress', 'translate_name': 'Đang làm', 'order': 2, 'is_edit': True,
                        'task_kind': 0,
                        'task_color': '#f9aab7'
                    },
                    {
                        'name': 'Completed', 'translate_name': 'Đã hoàn thành', 'order': 3, 'is_edit': False,
                        'task_kind': 2, 'task_color': '#f7e368'
                    },
                    {
                        'name': 'Pending', 'translate_name': 'Tạm ngưng', 'order': 4, 'is_edit': False, 'task_kind': 3,
                        'task_color': '#ff686d',
                    },
                ],
                'is_edit_date': False,
                'is_edit_est': False
            },
        )
        if created:
            temp_stt = []
            for item in config.list_status:
                temp_stt.append(
                    OpportunityTaskStatus(
                        tenant=config.tenant,
                        company=config.company,
                        title=item['name'],
                        translate_name=item['translate_name'],
                        task_config=config,
                        order=item['order'],
                        is_edit=item['is_edit'],
                        task_kind=item['task_kind'],
                        task_color=item['task_color'],
                    )
                )
            OpportunityTaskStatus.objects.bulk_create(temp_stt)

    def process_function_config(self):
        bulk_info = []
        for data in self.function_process_data:
            bulk_info.append(
                SaleFunction(
                    company=self.company_obj,
                    tenant=self.company_obj.tenant,
                    code='',
                    **data,
                )
            )
        SaleFunction.objects.bulk_create(bulk_info)

    def process_config(self):
        Process.objects.create(
            company=self.company_obj,
            tenant=self.company_obj.tenant,
            code='',
        )

    def leave_config(self, company_config):
        config, created = LeaveConfig.objects.get_or_create(
            company=self.company_obj,
            defaults={},
        )
        if not company_config:
            company_config = CompanyConfig.objects.get(company=self.company_obj)
        if created:
            #
            translation.activate(company_config.language if company_config else 'vi')
            default_list = [
                {
                    'code': 'MA', 'title': _('Maternity leave-social insurance'), 'paid_by': 2,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None, 'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'SC', 'title': _('Sick yours child-social insurance'), 'paid_by': 2,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None, 'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'SY', 'title': _('Sick yourself-social insurance'), 'paid_by': 2,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None, 'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'FF', 'title': _('Funeral your family (max 3 days)'), 'paid_by': 1,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None,
                    'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'MC', 'title': _('Marriage your child (max 1 days)'), 'paid_by': 1,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None,
                    'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'MY', 'title': _('Marriage yourself (max 3 days)'), 'paid_by': 1,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None,
                    'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'UP', 'title': _('Unpaid leave'), 'paid_by': 3,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None, 'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'ANPY', 'title': _('Annual leave-previous year balance'), 'paid_by': 1,
                    'balance_control': True, 'is_lt_system': True, 'is_lt_edit': True,
                    'is_check_expiration': False, 'data_expired': None, 'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'AN', 'title': _('Annual leave'), 'paid_by': 1,
                    'balance_control': True, 'is_lt_system': True, 'is_lt_edit': True,
                    'is_check_expiration': False, 'data_expired': None, 'no_of_paid': 12, 'prev_year': 0
                },
            ]
            temp_leave_type = []
            for item in default_list:
                temp_leave_type.append(
                    LeaveType(
                        company=config.company,
                        leave_config=config,
                        code=item['code'],
                        title=item['title'],
                        paid_by=item['paid_by'],
                        balance_control=item['balance_control'],
                        is_lt_system=item['is_lt_system'],
                        is_lt_edit=item['is_lt_edit'],
                        is_check_expiration=item['is_check_expiration'],
                        data_expired=item['data_expired'],
                        no_of_paid=item['no_of_paid'],
                        prev_year=item['prev_year'],
                    )
                )
            LeaveType.objects.bulk_create(temp_leave_type)

    def purchase_request_config(self):
        PurchaseRequestConfig.objects.create(
            employee_reference=[],
            company=self.company_obj,
            tenant=self.company_obj.tenant,
            code='',
        )

    def working_calendar_config(self):
        WorkingCalendarConfig.objects.get_or_create(
            company=self.company_obj,
            defaults={  # noqa
                'working_days':
                    {
                        0: {
                            'work': False,
                            'mor': {'from': '', 'to': ''},
                            'aft': {'from': '', 'to': ''}
                        },
                        1: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        2: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        3: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        4: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        5: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        6: {
                            'work': False,
                            'mor': {'from': '', 'to': ''},
                            'aft': {'from': '', 'to': ''}
                        },

                    }
            },
        )

    def asset_tools_config(self):
        AssetToolsConfig.objects.get_or_create(
            company=self.company_obj,
            defaults={
                'company': self.company_obj,
            },
        )

    def make_sure_workflow_apps(self):
        plan_ids = TenantPlan.objects.filter(tenant=self.company_obj.tenant).values_list('plan_id', flat=True)
        app_objs = [
            x.application for x in
            PlanApplication.objects.select_related('application').filter(plan_id__in=plan_ids)
        ]
        for obj in WorkflowConfigOfApp.objects.filter(application__is_workflow=False):
            print('delete Workflow Config App: ', obj.application, obj.company)
            obj.delete()
        for app in app_objs:
            if app.is_workflow is True:
                WorkflowConfigOfApp.objects.get_or_create(
                    company=self.company_obj,
                    application=app,
                    defaults={
                        'tenant': self.company_obj.tenant,
                        'workflow_currently': Workflow.objects.filter(
                            tenant=self.company_obj.tenant,
                            company=self.company_obj,
                            application=app,
                        ).first()
                    }
                )
        return True

    def call_new(self):
        config = self.company_config()
        self.delivery_config()
        self.quotation_config()
        self.sale_order_config()
        self.opportunity_config()
        self.opportunity_config_stage()
        self.quotation_indicator_config()
        self.sale_order_indicator_config()
        self.task_config()
        self.process_function_config()
        self.process_config()
        self.leave_config(config)
        self.purchase_request_config()
        self.working_calendar_config()
        self.asset_tools_config()
        self.make_sure_workflow_apps()
        return True


@receiver(post_save, sender=Company)
def update_stock(sender, instance, created, **kwargs):  # pylint: disable=W0613
    if created is True:
        ConfigDefaultData(company_obj=instance).call_new()
        SaleDefaultData(company_obj=instance)()


@receiver(pre_delete, sender=Notifications)
@receiver(post_save, sender=Notifications)
def clear_cache_notify(sender, instance, **kwargs):  # pylint: disable=W0613
    if getattr(instance, 'employee_id', None):
        Caching().delete(instance.cache_base_key(my_obj=instance))


@receiver(post_save, sender=RuntimeAssignee)
def handler_runtime_task_update(sender, instance, **kwargs):  # pylint: disable=W0613
    # update is_done notify when task assignee is done.
    if instance and getattr(instance, 'is_done', False) is True:
        stage_obj = instance.stage
        if stage_obj:
            runtime_obj = stage_obj.runtime
            if runtime_obj:
                obj = Notifications.objects.filter(
                    employee_id=instance.employee_id,
                    doc_id=runtime_obj.doc_id,
                    doc_app=runtime_obj.app_code,
                )
                obj.update(is_done=True)


# @receiver(pre_save, sender=Files)
# def move_media_file_to_folder_app(sender, instance, **kwargs):  # pylint: disable=W0613
#     MediaForceAPI.regis_link_to_file(
#         media_file_id=instance.media_file_id,
#         api_file_id=instance.id,
#         api_app_code=instance.relate_app_code,
#         media_user_id=instance.employee_created.media_user_id if instance.employee_created else None,
#     )
#
#
# @receiver(post_delete, sender=Files)
# def destroy_files(sender, instance, **kwargs):  # pylint: disable=W0613
#     MediaForceAPI.destroy_link_to_file(
#         media_file_id=instance.media_file_id,
#         api_file_id=instance.id,
#         api_app_code=instance.relate_app_code,
#         media_user_id=instance.employee_created.media_user_id if instance.employee_created else None,
#     )


@receiver(post_save, sender=RuntimeViewer)
def append_permission_viewer_runtime(sender, instance, created, **kwargs):
    if created:
        runtime = instance.runtime
        emp = instance.employee
        if runtime and emp:
            doc_id = runtime.doc_id
            app_obj = runtime.app
            if app_obj and doc_id:
                emp.append_permit_by_ids(
                    app_label=app_obj.app_label,
                    model_code=app_obj.code,
                    perm_code='view',
                    doc_id=str(doc_id),
                    tenant_id=instance.runtime.tenant_id,
                )
                # check if assignee has zones => append perm edit on doc_id
                if emp.all_runtime_assignee_of_employee.filter(
                        ~Q(zone_and_properties={}) & ~Q(zone_and_properties=[]),
                        stage__runtime=runtime,
                ).exists():
                    emp.append_permit_by_ids(
                        app_label=app_obj.app_label,
                        model_code=app_obj.code,
                        perm_code='edit',
                        doc_id=str(doc_id),
                        tenant_id=instance.runtime.tenant_id,
                    )


@receiver(post_save, sender=RuntimeAssignee)
def event_new_assignee_runtime(sender, instance, created, **kwargs):
    if created:
        instance.stage.runtime.append_viewer(instance.employee)


@receiver(post_save, sender=Runtime)
def event_new_runtime(sender, instance, created, **kwargs):
    if created:
        instance.append_viewer(instance.doc_employee_inherit)
        instance.append_viewer(instance.doc_employee_created)


@receiver(post_save, sender=OpportunitySaleTeamMember)
def opp_member_event_update(sender, instance, created, **kwargs):
    employee_obj = instance.member
    if employee_obj and hasattr(employee_obj, 'id'):
        employee_permission, _created = EmployeePermission.objects.get_or_create(employee=employee_obj)
        employee_permission.append_permit_by_opp(
            tenant_id=instance.opportunity.tenant_id,
            opp_id=instance.opportunity_id,
            perm_config=instance.permission_by_configured,
        )


@receiver(post_delete, sender=OpportunitySaleTeamMember)
def opp_member_event_destroy(sender, instance, **kwargs):
    employee_obj = instance.member
    if employee_obj and hasattr(employee_obj, 'id'):
        employee_permission, _created = EmployeePermission.objects.get_or_create(employee=employee_obj)
        employee_permission.remove_permit_by_opp(
            tenant_id=instance.opportunity.tenant_id, opp_id=instance.opportunity_id
        )


@receiver(pre_delete, sender=Role)
@receiver(pre_delete, sender=Employee)
def destroy_employee_or_role(sender, instance, **kwargs):
    if isinstance(instance, Role):
        call_task_background(
            sync_plan_app_employee,
            **{
                'employee_ids': [
                    str(ite) for ite in RoleHolder.objects.filter(role=instance).values_list('employee_id', flat=True)
                ],
            }
        )
    elif isinstance(instance, Employee):
        call_task_background(
            clear_cache_notify
        )
        call_task_background(
            uninstall_plan_app_employee,
            **{
                'employee_id': str(instance.id),
                'tenant_id': str(instance.tenant_id),
                'company_id': str(instance.company_id)
            }
        )


@receiver(post_save, sender=Role)
@receiver(post_save, sender=Employee)
def new_employee_or_role(sender, instance, created, **kwargs):
    if created is True:
        if isinstance(instance, Employee):
            EmployeePermission.objects.get_or_create(employee=instance)
        elif isinstance(instance, Role):
            RolePermission.objects.get_or_create(role=instance)


@receiver(post_save, sender=TaskResult)
def task_new_consumer(sender, instance, created, **kwargs):
    if instance.status in ('FAILURE', 'RETRY'):
        msg = TeleBotPushNotify.generate_msg(
            idx=instance.id,
            status=instance.status,
            group_name='CELERY_TASK',
            **{
                'task_name': instance.task_name,
                'date_created': TeleBotPushNotify.pretty_datetime(instance.date_created),
                'args': instance.task_args,
                'kwargs': instance.task_kwargs,
                'result': instance.result,
                'traceback': instance.traceback,
            }
        )
        TeleBotPushNotify().send_msg(msg=msg)
