import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.base.models import Currency as BaseCurrency
from apps.core.company.models import Company, CompanyConfig
from apps.masterdata.saledata.models.accounts import AccountType
from apps.masterdata.saledata.models.product import ProductType
from apps.masterdata.saledata.models.price import TaxCategory, Currency, Price

logger = logging.getLogger(__name__)


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
        {'title': 'Customer', 'code': 'AT001', 'is_default': 1},
        {'title': 'Supplier', 'code': 'AT002', 'is_default': 1},
        {'title': 'Partner', 'code': 'AT003', 'is_default': 1},
        {'title': 'Competitor', 'code': 'AT004', 'is_default': 1}
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
        objs = [
            Currency(tenant=self.company_obj.tenant, company=self.company_obj, **c_item)
            for c_item in self.Currency_data
        ]
        Currency.objects.bulk_create(objs)
        return True

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


@receiver(post_save, sender=Company)
def update_stock(sender, instance, created, **kwargs):  # pylint: disable=W0613
    if created is True:
        CompanyConfig.objects.create(
            company=instance,
            language='vi',
            currency=BaseCurrency.objects.get(code='VND'),
        )
        SaleDefaultData(company_obj=instance)()
