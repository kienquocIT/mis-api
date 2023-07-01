import logging

from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.core.log.models import Notifications
from apps.core.workflow.models import RuntimeAssignee
from apps.sales.opportunity.models import OpportunityConfig, OpportunityConfigStage, StageCondition
from apps.sales.quotation.models import QuotationAppConfig, ConfigShortSale, ConfigLongSale, QuotationIndicatorConfig, \
    IndicatorDefaultData
from apps.core.base.models import Currency as BaseCurrency
from apps.core.company.models import Company, CompanyConfig
from apps.masterdata.saledata.models import (
    AccountType, ProductType, TaxCategory, Currency, Price,
)
from apps.sales.delivery.models import DeliveryConfig
from apps.sales.saleorder.models import SaleOrderAppConfig, ConfigOrderLongSale, ConfigOrderShortSale
from apps.shared import Caching

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
            'win_rate': 0,
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

    def __init__(self, company_obj):
        self.company_obj = company_obj

    def company_config(self):
        CompanyConfig.objects.get_or_create(
            company=self.company_obj,
            defaults={
                'language': 'vi',
                'currency': BaseCurrency.objects.get(code='VND'),
            },
        )

    def delivery_config(self):
        DeliveryConfig.objects.get_or_create(
            company=self.company_obj,
            defaults={
                'is_picking': False,
                'is_partial_ship': False,
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
        for data in IndicatorDefaultData.INDICATOR_DATA:
            bulk_info.append(QuotationIndicatorConfig(
                company=self.company_obj,
                **data,
            ))
        QuotationIndicatorConfig.objects.bulk_create(bulk_info)

    def call_new(self):
        self.company_config()
        self.delivery_config()
        self.quotation_config()
        self.sale_order_config()
        self.opportunity_config()
        self.opportunity_config_stage()
        self.quotation_indicator_config()
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
