import json

from django.db import models

from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


class PurchaseRequestConfig(MasterDataAbstractModel):
    employee_reference = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                {
                    'id': 'emp_id',
                    'full_name': 'emp_full_name'
                }
            ]
        )
    )


class EmployeeReferenceEntireSaleOrder(SimpleAbstractModel):
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="reference_entire_sale_order",
    )
    purchase_request_config = models.ForeignKey(
        PurchaseRequestConfig,
        on_delete=models.CASCADE,
        related_name="purchase_request_config",
    )
