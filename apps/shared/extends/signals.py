import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.workflow.utils.runtime import (
    RuntimeHandler,
)
from apps.core.workflow.tasks import (
    call_new_runtime,
)
from apps.shared import call_task_background
from apps.core.base.models import Currency as BaseCurrency
from apps.core.company.models import Company, CompanyConfig
from apps.masterdata.saledata.models import (
    AccountType, ProductType, TaxCategory, Currency, Price,
    Account, Contact,
)
from apps.sales.delivery.models import DeliveryConfig
from apps.core.workflow.models import (
    Runtime,
)

logger = logging.getLogger(__name__)

__all__ = [
    'update_stock',
    'entry_run_workflow',
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

    def call_new(self):
        self.company_config()
        self.delivery_config()
        return True


@receiver(post_save, sender=Company)
def update_stock(sender, instance, created, **kwargs):  # pylint: disable=W0613
    if created is True:
        ConfigDefaultData(company_obj=instance).call_new()
        SaleDefaultData(company_obj=instance)()


@receiver(post_save, sender=Account)
@receiver(post_save, sender=Contact)
def entry_run_workflow(sender, instance, created, **kwargs):  # pylint: disable=W0613
    if instance.system_status == 1:
        if not instance.workflow_runtime_id:
            update_fields = kwargs.get('update_fields', [])
            if not (update_fields and len(update_fields) == 1 and 'workflow_runtime' in update_fields):
                if not Runtime.objects.filter(
                        tenant_id=instance.tenant_id, company_id=instance.company_id,
                        doc_id=instance.id, app_code=str(instance.__class__.get_model_code())
                ).exists():
                    runtime_obj = RuntimeHandler.create_runtime_obj(
                        tenant_id=str(instance.tenant_id), company_id=str(instance.company_id),
                        doc_id=str(instance.id), app_code=str(instance.__class__.get_model_code()),
                    )
                    call_task_background(
                        call_new_runtime,
                        *[str(runtime_obj.id)],
                    )
