import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.company.models import Company
from apps.sale.saledata.models.product import ProductType

logger = logging.getLogger(__name__)


class SaleDefaultData:
    ProductType_data = [
        {'title': 'Sản phẩm', 'is_default': 1},
        {'title': 'Bán thành phẩm', 'is_default': 1},
        {'title': 'Nguyên vật liệu', 'is_default': 1},
        {'title': 'Dịch vụ', 'is_default': 1},
    ]

    def __init__(self, company_obj):
        self.company_obj = company_obj

    def __call__(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.create_product_type()
            return True
        except Exception as err:
            logger.error(
                '[ERROR][SaleDefaultData]: Company ID=%s, Error=%s',
                str(self.company_obj.id), str(err)
            )
        return False

    def create_product_type(self):
        objs = [
            ProductType(tenant=self.company_obj.tenant, company=self.company_obj, **sal_item)
            for sal_item in self.ProductType_data
        ]
        ProductType.objects.bulk_create(objs)
        return True


@receiver(post_save, sender=Company)
def update_stock(sender, instance, **kwargs):  # pylint: disable=W0613
    SaleDefaultData(company_obj=instance)()
