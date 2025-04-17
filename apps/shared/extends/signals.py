import logging
from operator import truediv

from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import TaskResult

from apps.core.hr.models import Role, Employee, RoleHolder, EmployeePermission, RolePermission
from apps.core.hr.tasks import sync_plan_app_employee, uninstall_plan_app_employee
from apps.core.log.models import Notifications
from apps.core.process.models import Process, ProcessMembers  # SaleFunction
from apps.core.workflow.models import RuntimeAssignee, WorkflowConfigOfApp, Workflow
from apps.core.workflow.models.runtime import RuntimeViewer, Runtime
from apps.eoffice.leave.models import LeaveConfig, LeaveType, WorkingCalendarConfig
from apps.sales.opportunity.models import (
    OpportunityConfig, OpportunityConfigStage, StageCondition,
    OpportunitySaleTeamMember, Opportunity,
)
from apps.sales.purchasing.models import PurchaseRequestConfig
from apps.sales.quotation.models import (
    QuotationAppConfig, ConfigShortSale, ConfigLongSale, QuotationIndicatorConfig, SQIndicatorDefaultData,
)
from apps.core.base.models import Currency as BaseCurrency, PlanApplication, BaseItemUnit
from apps.core.company.models import Company, CompanyConfig, CompanyFunctionNumber
from apps.masterdata.saledata.models import (
    AccountType, ProductType, TaxCategory, Currency, Price, UnitOfMeasureGroup, PriceListCurrency, UnitOfMeasure,
    DocumentType, FixedAssetClassificationGroup, FixedAssetClassification, Tax, Salutation, Industry, AccountGroup,
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
from apps.core.tenant.models import TenantPlan

from apps.core.mailer.tasks import send_mail_otp, send_mail_new_project_member, send_mail_new_contract_submit
from apps.core.account.models import ValidateUser
from apps.eoffice.leave.leave_util import leave_available_map_employee
from apps.sales.lead.models import LeadStage
from apps.sales.project.models import ProjectMapMember, ProjectMapGroup, ProjectMapWork, ProjectConfig
from apps.core.forms.models import Form, FormPublishedEntries
from apps.core.forms.tasks import notifications_form_with_new, notifications_form_with_change
from apps.sales.project.extend_func import calc_rate_project, calc_update_task, re_calc_work_group
from .models import DisperseModel
from .. import ProjectMsg
from ...sales.leaseorder.models import LeaseOrderAppConfig
from ...sales.project.tasks import create_project_news

logger = logging.getLogger(__name__)

__all__ = [
    'SaleDefaultData',
    'ConfigDefaultData',
    'update_stock',
]


class SaleDefaultData:
    Salutation_data = [
        {'code': 'SA001', 'title': 'Anh', 'is_default': 1},
        {'code': 'SA002', 'title': 'Chị', 'is_default': 1},
        {'code': 'SA003', 'title': 'Ông', 'is_default': 1},
        {'code': 'SA004', 'title': 'Bà', 'is_default': 1}
    ]
    Account_types_data = [
        {'title': 'Customer', 'code': 'AT001', 'is_default': 1, 'account_type_order': 0},
        {'title': 'Supplier', 'code': 'AT002', 'is_default': 1, 'account_type_order': 1},
        {'title': 'Partner', 'code': 'AT003', 'is_default': 1, 'account_type_order': 2},
        {'title': 'Competitor', 'code': 'AT004', 'is_default': 1, 'account_type_order': 3}
    ]
    Account_groups_data = [
        {'code': 'AG001', 'title': 'Khách lẻ', 'is_default': 1},
        {'code': 'AG002', 'title': 'VIP1', 'is_default': 1},
        {'code': 'AG003', 'title': 'VIP2', 'is_default': 1},
    ]
    Industries_data = [
        {'code': 'IN001', 'title': 'Dịch vụ', 'is_default': 1},
        {'code': 'IN002', 'title': 'Sản xuất', 'is_default': 1},
        {'code': 'IN003', 'title': 'Phân phối', 'is_default': 1},
        {'code': 'IN004', 'title': 'Bán lẻ', 'is_default': 1},
        {'code': 'IN005', 'title': 'Giáo dục', 'is_default': 1},
        {'code': 'IN006', 'title': 'Y tế', 'is_default': 1},
    ]
    ProductType_data = [
        {'code': 'goods', 'title': 'Hàng hóa', 'is_default': 1, 'is_goods': 1},
        {'code': 'material', 'title': 'Nguyên vật liệu', 'is_default': 1, 'is_material': 1},
        {'code': 'finished_goods', 'title': 'Thành phẩm', 'is_default': 1, 'is_finished_goods': 1},
        {'code': 'tool', 'title': 'Công cụ - Dụng cụ', 'is_default': 1, 'is_tool': 1},
        {'code': 'service', 'title': 'Dịch vụ', 'is_default': 1, 'is_service': 1},
    ]
    UoM_Group_data = [
        {'code': 'ImportGroup', 'title': 'Nhóm đơn vị cho import', 'is_default': 1},
        {'code': 'Labor', 'title': 'Nhân công', 'is_default': 1},
        {'code': 'Size', 'title': 'Kích thước', 'is_default': 1},
        {'code': 'Time', 'title': 'Thời gian', 'is_default': 1},
        {'code': 'Unit', 'title': 'Đơn vị', 'is_default': 1},
    ]
    TaxCategory_data = [
        {'code': 'TC001', 'title': 'Thuế GTGT', 'is_default': 1},
        {'code': 'TC002', 'title': 'Thuế xuất khẩu', 'is_default': 1},
        {'code': 'TC003', 'title': 'Thuế nhập khẩu', 'is_default': 1},
        {'code': 'TC004', 'title': 'Thuế tiêu thụ đặc biệt', 'is_default': 1},
        {'code': 'TC005', 'title': 'Thuế nhà thầu', 'is_default': 1},
    ]
    Tax_data = [
        {'code': 'VAT_KCT', 'title': 'VAT-KCT', 'tax_type': 2, 'rate': 0, 'is_default': 1},
        {'code': 'VAT_0', 'title': 'VAT-0', 'tax_type': 2, 'rate': 0, 'is_default': 1},
        {'code': 'VAT_5', 'title': 'VAT-5', 'tax_type': 2, 'rate': 5, 'is_default': 1},
        {'code': 'VAT_8', 'title': 'VAT-8', 'tax_type': 2, 'rate': 8, 'is_default': 1},
        {'code': 'VAT_10', 'title': 'VAT-10', 'tax_type': 2, 'rate': 10, 'is_default': 1},
    ]
    Price_general_data = [
        {'title': 'General Price List', 'price_list_type': 0, 'factor': 1.0, 'is_default': 1}
    ]
    Document_Type_data = [
        {'code': 'BDT001', 'title': 'Đơn dự thầu', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT002', 'title': 'Tài liệu chứng minh tư cách pháp nhân', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT003', 'title': 'Giấy ủy quyền', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT004', 'title': 'Thỏa thuận liên doanh', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT005', 'title': 'Bảo đảm dự thầu', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT006', 'title': 'Tài liệu chứng minh năng lực nhà thầu', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT007', 'title': 'Đề xuất kĩ thuật', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT008', 'title': 'Đề xuất giá', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'CDT001', 'title': 'Tài liệu xác định yêu cầu', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'CDT002', 'title': 'Tài liệu giới thiệu sản phẩm', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'CDT003', 'title': 'Thuyết minh kĩ thuật', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'CDT004', 'title': 'Tài liệu đề xuất giải pháp', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'CDT005', 'title': 'BOM', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'CDT006', 'title': 'Giới thiệu dịch vụ hỗ trợ vận hành', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'CDT007', 'title': 'Thuyết trình phạm vi dự án', 'is_default': 0, 'doc_type_category': 'consulting'},
    ]
    Fixed_Asset_Group_data = [
        {'code': 'FACG001', 'title': 'Tài sản cố định hữu hình', 'is_default': 1},
        {'code': 'FACG002', 'title': 'Tài sản cố định vô hình', 'is_default': 1},
        {'code': 'FACG003', 'title': 'Tài sản cố định thuê tài chính', 'is_default': 1}
    ]
    Fixed_Asset_data = [
        {'code': 'FAC001', 'title': 'Nhà cửa, vật kiến trúc - quản lý', 'is_default': 1},
        {'code': 'FAC002', 'title': 'Máy móc thiết bị - sản xuất', 'is_default': 1},
        {'code': 'FAC003', 'title': 'Phương tiện vận tải, truyền dẫn - kinh doanh', 'is_default': 1},
        {'code': 'FAC004', 'title': 'Quyền sử dụng đất', 'is_default': 1},
        {'code': 'FAC005', 'title': 'Quyền phát hành', 'is_default': 1},
        {'code': 'FAC006', 'title': 'Bản quyền, bằng sáng chế', 'is_default': 1},
        {'code': 'FAC007', 'title': 'TSCD hữu hình thuê tài chính', 'is_default': 1},
        {'code': 'FAC008', 'title': 'TSCD vô hình thuê tài chính', 'is_default': 1},
    ]

    def __init__(self, company_obj):
        self.company_obj = company_obj

    def __call__(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.create_company_function_number()
                self.create_salutation()
                self.create_account_types()
                self.create_account_group()
                self.create_industry()
                self.create_product_type()
                self.create_uom_group_and_uom()
                self.create_tax_category()
                self.create_tax()
                self.create_currency()
                self.create_price_default()
                self.create_document_types()
                self.create_fixed_asset_masterdata()
            return True
        except Exception as err:
            logger.error(
                '[ERROR][SaleDefaultData]: Company ID=%s, Error=%s',
                str(self.company_obj.id), str(err)
            )
        return False

    def create_company_function_number(self):
        objs = []
        for cf_item in range(0, 10):
            objs.append(
                CompanyFunctionNumber(
                    company=self.company_obj,
                    function=cf_item,
                    numbering_by=0
                )
            )
        CompanyFunctionNumber.objects.bulk_create(objs)
        return True

    def create_salutation(self):
        objs = [
            Salutation(tenant=self.company_obj.tenant, company=self.company_obj, **item)
            for item in self.Salutation_data
        ]
        Salutation.objects.bulk_create(objs)
        return True

    def create_account_types(self):
        objs = [
            AccountType(tenant=self.company_obj.tenant, company=self.company_obj, **at_item)
            for at_item in self.Account_types_data
        ]
        AccountType.objects.bulk_create(objs)
        return True

    def create_account_group(self):
        objs = [
            AccountGroup(tenant=self.company_obj.tenant, company=self.company_obj, **item)
            for item in self.Account_groups_data
        ]
        AccountGroup.objects.bulk_create(objs)
        return True

    def create_industry(self):
        objs = [
            Industry(tenant=self.company_obj.tenant, company=self.company_obj, **item)
            for item in self.Industries_data
        ]
        Industry.objects.bulk_create(objs)
        return True

    def create_product_type(self):
        objs = [
            ProductType(tenant=self.company_obj.tenant, company=self.company_obj, **pt_item)
            for pt_item in self.ProductType_data
        ]
        ProductType.objects.bulk_create(objs)
        return True

    def create_uom_group_and_uom(self):
        objs = [
            UnitOfMeasureGroup(tenant=self.company_obj.tenant, company=self.company_obj, **uom_group_item)
            for uom_group_item in self.UoM_Group_data
        ]
        UnitOfMeasureGroup.objects.bulk_create(objs)

        unit_group = UnitOfMeasureGroup.objects.filter(
            tenant=self.company_obj.tenant, company=self.company_obj, code='Unit', is_default=1
        ).first()
        if unit_group:
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='UOM001',
                title='Cái',
                is_referenced_unit=1,
                ratio=1,
                rounding=4,
                is_default=1,
                group=unit_group
            )
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='UOM002',
                title='Con',
                is_referenced_unit=1,
                ratio=1,
                rounding=4,
                is_default=1,
                group=unit_group
            )
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='UOM003',
                title='Thanh',
                is_referenced_unit=1,
                ratio=1,
                rounding=4,
                is_default=1,
                group=unit_group
            )
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='UOM004',
                title='Lần',
                is_referenced_unit=1,
                ratio=1,
                rounding=4,
                is_default=1,
                group=unit_group
            )
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='UOM005',
                title='Gói',
                is_referenced_unit=1,
                ratio=1,
                rounding=4,
                is_default=1,
                group=unit_group
            )


        # add default uom for group time
        labor_group = UnitOfMeasureGroup.objects.filter(
            tenant=self.company_obj.tenant, company=self.company_obj, code='Labor', is_default=1
        ).first()
        if labor_group:
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='Manhour',
                title='Manhour',
                is_referenced_unit=1,
                ratio=1,
                rounding=4,
                is_default=1,
                group=labor_group
            )
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='Manday',
                title='Manday',
                is_referenced_unit=0,
                ratio=8,
                rounding=4,
                is_default=1,
                group=labor_group
            )
            UnitOfMeasure.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                code='Manmonth',
                title='Manmonth',
                is_referenced_unit=0,
                ratio=176,
                rounding=4,
                is_default=1,
                group=labor_group
            )
        return True

    def create_tax_category(self):
        objs = [
            TaxCategory(tenant=self.company_obj.tenant, company=self.company_obj, **tc_item)
            for tc_item in self.TaxCategory_data
        ]
        TaxCategory.objects.bulk_create(objs)
        return True

    def create_tax(self):
        # get tax category
        vat_tax_category = TaxCategory.objects.filter(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            code='TC001'
        ).first()

        if vat_tax_category:
            objs = [
                Tax(tenant=self.company_obj.tenant, company=self.company_obj, category=vat_tax_category, **item)
                for item in self.Tax_data
            ]
            Tax.objects.bulk_create(objs)
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
                        is_primary=primary,
                        is_default=True
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
            general_pr = Price.objects.create(
                tenant=self.company_obj.tenant, company=self.company_obj, currency=[primary_current_id],
                **self.Price_general_data[0]
            )
            PriceListCurrency.objects.create(price=general_pr, currency_id=primary_current_id)
            return True
        return False

    def create_document_types(self):
        objs = [
            DocumentType(tenant=self.company_obj.tenant, company=self.company_obj, **item)
            for item in self.Document_Type_data
        ]
        DocumentType.objects.bulk_create(objs)
        return True

    def create_fixed_asset_masterdata(self):
        # tai san co dinh huu hinh
        tangible_fixed_asset_group_instance = FixedAssetClassificationGroup.objects.create(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            **self.Fixed_Asset_Group_data[0]
        )

        # tai san co dinh vo hinh
        intangible_fixed_asset_group_instance =  FixedAssetClassificationGroup.objects.create(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            **self.Fixed_Asset_Group_data[1]
        )

        # tai san co dinh thue tai chinh
        finance_leasing_fixed_asset_group_instance = FixedAssetClassificationGroup.objects.create(
            tenant=self.company_obj.tenant,
            company=self.company_obj,
            **self.Fixed_Asset_Group_data[2]
        )

        #create asset classification
        for index, data in enumerate(self.Fixed_Asset_data):
            if index < 3:
                # First 3 items belong to tangible_fixed_asset_group_instance
                group_instance = tangible_fixed_asset_group_instance
            elif index < 6:
                # Next 3 items belong to intangible_fixed_asset_group_instance
                group_instance = intangible_fixed_asset_group_instance
            else:
                # Last 2 items belong to finance_leasing_fixed_asset_group_instance
                group_instance = finance_leasing_fixed_asset_group_instance

            # Create FixedAssetClassification instance
            FixedAssetClassification.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                group=group_instance,  # Assign the group
                **data
            )
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
            'is_delete': False,
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
            'is_delete': False,
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
                        'title': 'Decision Maker'
                    },  # application property Decision Maker
                    'comparison_operator': '≠',
                    'compare_data': 0,
                },
                {
                    'condition_property': {
                        'id': '39b50254-e32d-473b-8380-f3b7765af434',
                        'title': 'Product Line Detail'
                    },  # application property Product Line Detail
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
            'is_delete': False,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'acab2c1e-74f2-421b-8838-7aa55c217f72',
                        'title': 'Quotation Status'
                    },  # application property Quotation Status
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
                        'title': 'SaleOrder Status'
                    },  # application property SaleOrder Status
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
                        'title': 'Competitor Win'
                    },  # application property Competitor Win
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
            'is_delete': False,
            'condition_datas': [
                {
                    'condition_property': {
                        'id': 'b5aa8550-7fc5-4cb8-a952-b6904b2599e5',
                        'title': 'SaleOrder Delivery Status'
                    },  # application property SaleOrder Delivery Status
                    'comparison_operator': '=',
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

    lead_stage_data = [
        {
            'stage_title': 'Marketing Acquired Lead',
            'level': 1,
        },
        {
            'stage_title': 'Marketing Qualified Lead',
            'level': 2,
        },
        {
            'stage_title': 'Sales Accepted Lead',
            'level': 3,
        },
        {
            'stage_title': 'Sales Qualified Lead',
            'level': 4,
        },
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
        base_currency = BaseCurrency.objects.filter(
            code=self.company_obj.currency_mapped.abbreviation
        ).first() if self.company_obj.currency_mapped else None
        if base_currency:
            obj, _created = CompanyConfig.objects.get_or_create(
                company=self.company_obj,
                defaults={
                    'language': 'vi',
                    'currency': base_currency,
                    'master_data_currency': self.company_obj.currency_mapped,
                },
            )
        else:
            print('\tCan not found Base Currency')
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

    def lead_stage(self):
        for stage in self.lead_stage_data:
            LeadStage.objects.create(
                tenant=self.company_obj.tenant,
                company=self.company_obj,
                **stage
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
                        'task_color': '#abe3e5', 'is_finish': False
                    },
                    {
                        'name': 'In Progress', 'translate_name': 'Đang làm', 'order': 2, 'is_edit': True,
                        'task_kind': 0, 'task_color': '#f9aab7', 'is_finish': False
                    },
                    {
                        'name': 'Completed', 'translate_name': 'Đã hoàn thành', 'order': 3, 'is_edit': False,
                        'task_kind': 2, 'task_color': '#f7e368', 'is_finish': True
                    },
                    {
                        'name': 'Pending', 'translate_name': 'Tạm ngưng', 'order': 4, 'is_edit': False, 'task_kind': 3,
                        'task_color': '#ff686d', 'is_finish': False
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
                        is_finish=False if item['task_kind'] != 2 else True
                    )
                )
            OpportunityTaskStatus.objects.bulk_create(temp_stt)

    def process_function_config(self):
        bulk_info = []
        # for data in self.function_process_data:
        #     bulk_info.append(
        #         SaleFunction(
        #             company=self.company_obj,
        #             tenant=self.company_obj.tenant,
        #             code='',
        #             **data,
        #         )
        #     )
        # SaleFunction.objects.bulk_create(bulk_info)

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
                    'code': 'SY', 'title': _('Sick leave for yourself-social insurance'), 'paid_by': 2,
                    'balance_control': False, 'is_lt_system': True, 'is_lt_edit': False,
                    'is_check_expiration': False, 'data_expired': None, 'no_of_paid': 0, 'prev_year': 0
                },
                {
                    'code': 'FF', 'title': _('Funeral in your family (max 3 days)'), 'paid_by': 1,
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
                    'code': 'MY', 'title': _('Your own marriage (max 3 days)'), 'paid_by': 1,
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

    def make_sure_workflow_apps(self):
        plan_ids = TenantPlan.objects.filter(tenant=self.company_obj.tenant).values_list('plan_id', flat=True)
        app_objs = [
            x.application for x in
            PlanApplication.objects.select_related('application').filter(plan_id__in=plan_ids)
        ]
        # Xóa WF config của app tắt is_workflow trong data config application
        for obj in WorkflowConfigOfApp.objects.filter(application__is_workflow=False):
            print('delete Workflow Config App: ', obj.application, obj.company)
            obj.delete()
        # Tạo mới WF config cho app bật is_workflow trong data config application
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

    def project_config(self):
        ProjectConfig.objects.create(
            company=self.company_obj,
            tenant=self.company_obj.tenant
        )

    def lease_order_config(self):
        LeaseOrderAppConfig.objects.create(
            company=self.company_obj,
            tenant=self.company_obj.tenant
        )

    def call_new(self):
        config = self.company_config()
        self.delivery_config()
        self.quotation_config()
        self.sale_order_config()
        self.opportunity_config()
        self.opportunity_config_stage()
        self.lead_stage()
        self.quotation_indicator_config()
        self.sale_order_indicator_config()
        self.task_config()
        self.process_function_config()
        self.process_config()
        self.leave_config(config)
        self.purchase_request_config()
        self.working_calendar_config()
        self.make_sure_workflow_apps()
        self.project_config()
        self.lease_order_config()
        return True


@receiver(post_save, sender=TaskResult)
def update_task_result(sender, instance, created, **kwargs):
    status = getattr(instance, 'status', '')
    if status == 'FAILURE':
        msg = TeleBotPushNotify.generate_msg(
            idx='CELERY_TASK',
            status='FAILURE',
            group_name='INFO',
            **{
                'id': str(getattr(instance, 'id', '-')),
                'task_id': str(getattr(instance, 'task_id', '-')),
                'task_name': str(getattr(instance, 'task_name', '-')),
                'task_kwargs': str(getattr(instance, 'task_kwargs', '-')),
                'task_args': str(getattr(instance, 'task_args', '-')),
                'date_created': str(getattr(instance, 'date_created', '-')),
                'date_done': str(getattr(instance, 'date_done', '-')),
                'trace_back': '-',
                'errors': str(getattr(instance, 'result', '-')),
            }
        )
        TeleBotPushNotify().send_msg(msg=msg)


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

        # handle sync member opp to process
        opp = instance.opportunity
        if opp and opp.process:
            ProcessMembers.objects.get_or_create(
                tenant=opp.tenant,
                company=opp.company,
                process=opp.process,
                employee=employee_obj,
                is_system=True,
            )


@receiver(post_delete, sender=OpportunitySaleTeamMember)
def opp_member_event_destroy(sender, instance, **kwargs):
    employee_obj = instance.member
    if employee_obj and hasattr(employee_obj, 'id'):
        employee_permission, _created = EmployeePermission.objects.get_or_create(employee=employee_obj)
        employee_permission.remove_permit_by_opp(
            tenant_id=instance.opportunity.tenant_id, opp_id=instance.opportunity_id
        )

        # handle sync member opp to process
        opp = instance.opportunity
        if opp and opp.process:
            try:
                obj = ProcessMembers.objects.get(
                    tenant=opp.tenant,
                    company=opp.company,
                    process=opp.process,
                    employee=employee_obj,
                    is_system=True,
                )
                obj.delete()
            except ProcessMembers.DoesNotExist:
                pass


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


@receiver(post_save, sender=Employee)
def new_employee(sender, instance, created, **kwargs):
    if created is True:
        leave_available_map_employee(instance, instance.company)


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


@receiver(post_save, sender=ValidateUser)
def task_validate_user_otp(sender, instance, created, **kwargs):
    if created is True:
        call_task_background(
            my_task=send_mail_otp,
            tenant_id=instance.user.tenant_current_id,
            company_id=instance.user.company_current_id,
            user_id=instance.user_id,
            otp_id=instance.id,
            otp=instance.otp,
        )


@receiver(post_save, sender=ProjectMapMember)
def project_member_event_update(sender, instance, created, **kwargs):
    employee_obj = instance.member
    project = instance.project
    company = project.company
    tenant = project.tenant

    if employee_obj and hasattr(employee_obj, 'id'):
        employee_permission, _created = EmployeePermission.objects.get_or_create(employee=employee_obj)
        employee_permission.append_permit_by_prj(
            tenant_id=instance.project.tenant_id,
            prj_id=str(instance.project_id),
            perm_config=instance.permission_by_configured,
        )
    if created and project.employee_inherit_id != employee_obj.id:
        mail_config_cls = DisperseModel(app_model='mailer.MailConfig').get_model()
        if mail_config_cls and hasattr(mail_config_cls, 'get_config'):
            config_obj = mail_config_cls.get_config(
                tenant_id=str(tenant.id), company_id=str(company.id)
            )
            if config_obj and config_obj.is_active:
                call_task_background(
                    my_task=send_mail_new_project_member,
                    **{
                        'tenant_id': str(tenant.id),
                        'company_id': str(company.id),
                        'prj_owner': str(project.employee_inherit_id),
                        'prj_member': str(employee_obj.id),
                        'prj_id': str(project.id),
                    }
                )


@receiver(post_delete, sender=ProjectMapMember)
def project_member_event_destroy(sender, instance, **kwargs):
    employee_obj = instance.member
    if employee_obj and hasattr(employee_obj, 'id'):
        employee_permission, _created = EmployeePermission.objects.get_or_create(employee=employee_obj)
        employee_permission.remove_permit_by_prj(
            tenant_id=instance.project.tenant_id, prj_id=instance.project_id
        )


@receiver(post_save, sender=Form)
def form_post_save(sender, instance, created, **kwargs):
    if created is True:
        instance.get_or_create_publish()


@receiver(post_save, sender=FormPublishedEntries)
def new_entry_form_publish(sender, instance, created, **kwargs):
    published = getattr(instance, 'published', None)
    if published:
        notifications = getattr(published, 'notifications', {})
        if notifications:
            user_management_enable_new = notifications.get('user_management_enable_new', False)
            creator_enable_new = notifications.get('creator_enable_new', False)
            user_management_enable_change = notifications.get('user_management_enable_change', False)
            creator_enable_change = notifications.get('creator_enable_change', False)

            if created:
                if user_management_enable_new or creator_enable_new:
                    call_task_background(
                        my_task=notifications_form_with_new,
                        **{
                            'entry_id': str(instance.id),
                        }
                    )
            else:
                if user_management_enable_change or creator_enable_change:
                    call_task_background(
                        my_task=notifications_form_with_change,
                        **{
                            'entry_id': str(instance.id),
                        },
                    )


@receiver(post_delete, sender=ProjectMapGroup)
def project_group_event_destroy(sender, instance, **kwargs):
    calc_rate_project(instance.project)
    print('re calculator weight id Done')


@receiver(post_delete, sender=ProjectMapWork)
def project_work_event_destroy(sender, instance, **kwargs):
    re_calc_work_group(instance.work)
    calc_rate_project(instance.project, instance)

    # create activities when delete works
    call_task_background(
        my_task=create_project_news,
        **{
            'project_id': str(instance.project.id),
            'employee_inherit_id': str(instance.work.employee_inherit.id),
            'employee_created_id': str(instance.work.employee_created.id),
            'application_id': str('49fe2eb9-39cd-44af-b74a-f690d7b61b67'),
            'document_id': str(instance.work.id),
            'document_title': str(instance.work.title),
            'title': ProjectMsg.DELETED_A,
            'msg': '',
        }
    )
    print('re calculator rate is Done')
