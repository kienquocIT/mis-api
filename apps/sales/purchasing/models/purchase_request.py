# from django.db import models
# from django.utils.translation import gettext_lazy as _
#
# from apps.shared import DataAbstractModel, SimpleAbstractModel
#
# REQUEST_FOR = [
#     (0, _('For Sale Order')),
#     (1, _('For Stock')),
#     (2, _('For Other')),
# ]
#
# PURCHASE_STATUS = [
#     (0, _('Wait')),
#     (1, _('Partially ordered')),
#     (2, _('Ordered')),
# ]
#
#
# class PurchaseRequest(DataAbstractModel):
#     sale_order = models.ForeignKey(
#         'saleorder.SaleOrder',
#         on_delete=models.CASCADE,
#         related_name="sale_order",
#     )
#
#     supplier = models.ForeignKey(
#         'saledata.Account',
#         on_delete=models.CASCADE,
#         related_name="purchase_supplier",
#     )
#     request_for = models.SmallIntegerField(
#         choices=REQUEST_FOR,
#         default=0
#     )
#     contact = models.ForeignKey(
#         'saledata.Contact',
#         on_delete=models.CASCADE,
#         related_name="purchase_contact",
#     )
#
#     delivered_date = models.DateTimeField(
#         help_text='Deadline for delivery'
#     )
#     purchase_status = models.SmallIntegerField(
#         choices=PURCHASE_STATUS,
#         default=0
#     )
#
#     note = models.CharField(
#         max_length=1000
#     )
#
#     purchase_product_datas = models.JSONField(
#         default=list,
#         help_text="read data product, use for get list or detail purchase",
#     )
