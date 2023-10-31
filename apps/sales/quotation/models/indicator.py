from django.db import models

from apps.shared import MasterDataAbstractModel, StringHandler


class QuotationIndicatorConfig(MasterDataAbstractModel):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.SET_NULL,
        null=True,
        related_name='indicator_company',
    )
    title = models.CharField(
        max_length=100,
        blank=True
    )
    remark = models.CharField(
        max_length=200,
        blank=True
    )
    example = models.CharField(
        max_length=300,
        blank=True
    )
    application_code = models.CharField(
        max_length=100,
        blank=True
    )
    formula_data = models.JSONField(default=list)
    formula_data_show = models.TextField(
        blank=True,
        null=True
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Quotation Indicator Config'
        verbose_name_plural = 'Quotation Indicator Configs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("IN")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = 'IN0001-' + StringHandler.random_str(17)
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'IN{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code(self.company_id)

        # hit DB
        super().save(*args, **kwargs)


class QuotationIndicator(MasterDataAbstractModel):
    quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_indicator_quotation",
    )
    indicator = models.ForeignKey(
        QuotationIndicatorConfig,
        on_delete=models.CASCADE,
        verbose_name="indicator",
        related_name="quotation_indicator_indicator",
    )
    indicator_value = models.FloatField(
        default=0,
        help_text="value of specific indicator for quotation"
    )
    indicator_rate = models.FloatField(
        default=0,
        help_text="rate value of specific indicator for quotation"
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Quotation Indicator'
        verbose_name_plural = 'Quotation Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class SQIndicatorDefaultData:
    INDICATOR_DATA = [
        {
            "title": "Revenue",
            "code": "IN0001",
            "remark": "Revenue",
            "example": "indicator(Revenue)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "9a8bef37-6812-4d8b-ba6a-dc5669e61029",
                    "code": "total_product_revenue_before_tax",
                    "type": 6,
                    "title": "Total revenue before tax",
                    "remark": "Total revenue before tax of quotation (after discount on total, apply promotion,...)",
                    "syntax": "prop(Total revenue before tax)",
                    "properties": {},
                    "is_property": True,
                    "syntax_show": "prop(Total revenue before tax)",
                    "content_type": "quotation.Quotation",
                }
            ],
            "formula_data_show": "prop(Total revenue before tax)",
            "order": 1
        },
        {
            "title": "Total cost",
            "code": "IN0002",
            "remark": "Total cost",
            "example": "indicator(Total cost)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "d1dcd149-6fc8-4234-870d-29497f8cfb88",
                    "code": "total_cost_pretax_amount",
                    "type": 6,
                    "title": "Total cost before tax",
                    "remark": "Total cost before tax of quotation",
                    "syntax": "prop(Total cost before tax)",
                    "properties": {},
                    "is_property": True,
                    "syntax_show": "prop(Total cost before tax)",
                    "content_type": "quotation.Quotation",
                }
            ],
            "formula_data_show": "prop(Total cost before tax)",
            "order": 2
        },
        {
            "title": "Gross profit",
            "code": "IN0003",
            "remark": "Gross profit",
            "example": "indicator(Gross profit)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "1",
                    "order": 1,
                    "title": "Revenue",
                    "remark": "Revenue",
                    "syntax": "indicator(Revenue)",
                    "example": "indicator(Revenue)",
                    "syntax_show": "indicator(Revenue)",
                    "formula_data": [
                        {
                            "id": "9a8bef37-6812-4d8b-ba6a-dc5669e61029",
                            "code": "total_product_revenue_before_tax",
                            "type": 6,
                            "title": "Total revenue before tax",
                            "remark": "Total revenue before tax of quotation "
                                      "(after discount on total, apply promotion,...)",
                            "syntax": "prop(Total revenue before tax)",
                            "properties": {},
                            "is_property": True,
                            "syntax_show": "prop(Total revenue before tax)",
                            "content_type": "quotation.Quotation",
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show": "prop(Total revenue before tax)"
                },
                "-",
                {
                    "id": "2",
                    "order": 2,
                    "title": "Total cost",
                    "remark": "Total cost",
                    "syntax": "indicator(Total cost)",
                    "example": "indicator(Total cost)",
                    "syntax_show": "indicator(Total cost)",
                    "formula_data": [
                        {
                            "id": "d1dcd149-6fc8-4234-870d-29497f8cfb88",
                            "code": "total_cost_pretax_amount",
                            "type": 6,
                            "title": "Total cost before tax",
                            "remark": "Total cost before tax of quotation",
                            "syntax": "prop(Total cost before tax)",
                            "properties": {},
                            "is_property": True,
                            "syntax_show": "prop(Total cost before tax)",
                            "content_type": "quotation.Quotation",
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show": "prop(Total cost before tax)"
                }
            ],
            "formula_data_show": "indicator(Revenue) - indicator(Total cost)",
            "order": 3
        },
        {
            "title": "Operating expense",
            "code": "IN0004",
            "remark": "Operating expense",
            "example": "indicator(Operating expense)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "aebaf647-49ff-4d59-a738-41ed6a583b50",
                    "code": "sumItemIf",
                    "title": "sumItemIf",
                    "remark": "Returns total of items that pass condition.",
                    "syntax": "sumItemIf(",
                    "example": "sumItemIf((5, 2, 9, 3), '>3') == 14",
                    "param_type": 2,
                    "syntax_show": "sumItemIf(item_check_list, condition, item_sum_list)",
                    "function_data": [
                        {
                            "id": "8ecc50e2-e7d6-4b0d-9cd5-92eec83f8f95",
                            "code": "expense_type_title",
                            "type": 1,
                            "title": "Expense type",
                            "remark": "Type expense on quotation expense line",
                            "syntax": "prop(Expense type)",
                            "properties": {},
                            "is_property": True,
                            "syntax_show": "prop(Expense type)",
                            "content_type": None,
                        },
                        "===",
                        "chiphítriểnkhai",
                        {
                            "id": "f0251c13-0480-4ac1-94d3-ebe03afb93bf",
                            "code": "expense_subtotal_price",
                            "type": 6,
                            "title": "Expense subtotal before tax",
                            "remark": "Subtotal before tax expense on quotation expense line",
                            "syntax": "prop(Expense subtotal before tax)",
                            "properties": {},
                            "is_property": True,
                            "syntax_show": "prop(Expense subtotal before tax)",
                            "content_type": None,
                        }
                    ]
                }
            ],
            "formula_data_show":
                'sumItemIf(prop(Expense type)=="Chi phí triển khai",prop(Expense subtotal before tax))',
            "order": 4
        },
        {
            "title": "Other expenses",
            "code": "IN0005",
            "remark": "Other expenses",
            "example": "indicator(Other expenses)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "490ecfee-30d2-468a-b075-84d44b8b150e",
                    "code": "total_expense_pretax_amount",
                    "type": 6,
                    "title": "Total expense before tax",
                    "remark": "Total expense before tax of quotation",
                    "syntax": "prop(Total expense before tax)",
                    "properties": {},
                    "is_property": True,
                    "syntax_show": "prop(Total expense before tax)",
                    "content_type": "quotation.Quotation",
                },
                "-",
                {
                    "id": "4",
                    "order": 4,
                    "title": "Operating expense",
                    "remark": "Operating expense",
                    "syntax": "indicator(Operating expense)",
                    "example": "indicator(Operating expense)",
                    "syntax_show": "indicator(Operating expense)",
                    "formula_data": [
                        {
                            "id": "aebaf647-49ff-4d59-a738-41ed6a583b50",
                            "code": "sumItemIf",
                            "title": "sumItemIf",
                            "remark": "Returns total of items that pass condition.",
                            "syntax": "sumItemIf(",
                            "example": "sumItemIf((5, 2, 9, 3), '>3') == 14",
                            "param_type": 2,
                            "syntax_show": "sumItemIf(item_check_list, condition, item_sum_list)",
                            "function_data": [
                                {
                                    "id": "8ecc50e2-e7d6-4b0d-9cd5-92eec83f8f95",
                                    "code": "expense_type_title",
                                    "type": 1,
                                    "title": "Expense type",
                                    "remark": "Type expense on quotation expense line",
                                    "syntax": "prop(Expense type)",
                                    "properties": {

                                    },
                                    "is_property": True,
                                    "syntax_show": "prop(Expense type)",
                                    "content_type": None
                                },
                                "===",
                                "chiphítriểnkhai",
                                {
                                    "id": "f0251c13-0480-4ac1-94d3-ebe03afb93bf",
                                    "code": "expense_subtotal_price",
                                    "type": 6,
                                    "title": "Expense subtotal before tax",
                                    "remark": "Subtotal before tax expense on quotation expense line",
                                    "syntax": "prop(Expense subtotal before tax)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Expense subtotal before tax)",
                                    "content_type": None
                                }
                            ]
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show":
                        'sumItemIf(prop(Expense type)=="Chi phí triển khai",prop(Expense subtotal before tax))',
                }
            ],
            "formula_data_show": 'prop(Total expense before tax) - indicator(Operating expense)',
            "order": 5
        },
        {
            "title": "Net income",
            "code": "IN0006",
            "remark": "Net income",
            "example": "indicator(Net income)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "3",
                    "order": 3,
                    "title": "Gross profit",
                    "remark": "Gross profit",
                    "syntax": "indicator(Gross profit)",
                    "example": "indicator(Gross profit)",
                    "syntax_show": "indicator(Gross profit)",
                    "formula_data": [
                        {
                            "id": "1",
                            "order": 1,
                            "title": "Revenue",
                            "remark": "Revenue",
                            "syntax": "indicator(Revenue)",
                            "example": "indicator(Revenue)",
                            "syntax_show": "indicator(Revenue)",
                            "formula_data": [
                                {
                                    "id": "9a8bef37-6812-4d8b-ba6a-dc5669e61029",
                                    "code": "total_product_revenue_before_tax",
                                    "type": 6,
                                    "title": "Total revenue before tax",
                                    "remark": "Total revenue before tax of quotation "
                                              "(after discount on total, apply promotion,...)",
                                    "syntax": "prop(Total revenue before tax)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Total revenue before tax)",
                                    "content_type": "quotation.Quotation",
                                }
                            ],
                            "is_indicator": True,
                            "formula_data_show": "prop(Total revenue before tax)"
                        },
                        "-",
                        {
                            "id": "2",
                            "order": 2,
                            "title": "Total cost",
                            "remark": "Total cost",
                            "syntax": "indicator(Total cost)",
                            "example": "indicator(Total cost)",
                            "syntax_show": "indicator(Total cost)",
                            "formula_data": [
                                {
                                    "id": "d1dcd149-6fc8-4234-870d-29497f8cfb88",
                                    "code": "total_cost_pretax_amount",
                                    "type": 6,
                                    "title": "Total cost before tax",
                                    "remark": "Total cost before tax of quotation",
                                    "syntax": "prop(Total cost before tax)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Total cost before tax)",
                                    "content_type": "quotation.Quotation",
                                }
                            ],
                            "is_indicator": True,
                            "formula_data_show": "prop(Total cost before tax)"
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show": "indicator(Revenue) - indicator(Total cost)"
                },
                "-",
                {
                    "id": "4",
                    "order": 4,
                    "title": "Operating expense",
                    "remark": "Operating expense",
                    "syntax": "indicator(Operating expense)",
                    "example": "indicator(Operating expense)",
                    "syntax_show": "indicator(Operating expense)",
                    "formula_data": [
                        {
                            "id": "aebaf647-49ff-4d59-a738-41ed6a583b50",
                            "code": "sumItemIf",
                            "title": "sumItemIf",
                            "remark": "Returns total of items that pass condition.",
                            "syntax": "sumItemIf(",
                            "example": "sumItemIf((5, 2, 9, 3), '>3') == 14",
                            "param_type": 2,
                            "syntax_show": "sumItemIf(item_check_list, condition, item_sum_list)",
                            "function_data": [
                                {
                                    "id": "8ecc50e2-e7d6-4b0d-9cd5-92eec83f8f95",
                                    "code": "expense_type_title",
                                    "type": 1,
                                    "title": "Expense type",
                                    "remark": "Type expense on quotation expense line",
                                    "syntax": "prop(Expense type)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Expense type)",
                                    "content_type": None,
                                },
                                "===",
                                "chiphítriểnkhai",
                                {
                                    "id": "f0251c13-0480-4ac1-94d3-ebe03afb93bf",
                                    "code": "expense_subtotal_price",
                                    "type": 6,
                                    "title": "Expense subtotal before tax",
                                    "remark": "Subtotal before tax expense on quotation expense line",
                                    "syntax": "prop(Expense subtotal before tax)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Expense subtotal before tax)",
                                    "content_type": None,
                                }
                            ]
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show":
                        'sumItemIf(prop(Expense type)=="Chi phí triển khai",prop(Expense subtotal before tax))'
                },
                "-",
                {
                    "id": "5",
                    "order": 5,
                    "title": "Other expenses",
                    "remark": "Other expenses",
                    "syntax": "indicator(Other expenses)",
                    "example": "indicator(Other expenses)",
                    "syntax_show": "indicator(Other expenses)",
                    "formula_data": [
                        {
                            "id": "490ecfee-30d2-468a-b075-84d44b8b150e",
                            "code": "total_expense_pretax_amount",
                            "type": 6,
                            "title": "Total expense before tax",
                            "remark": "Total expense before tax of quotation",
                            "syntax": "prop(Total expense before tax)",
                            "properties": {},
                            "is_property": True,
                            "syntax_show": "prop(Total expense before tax)",
                            "content_type": "quotation.Quotation",
                        },
                        "-",
                        {
                            "id": "62fca217-1985-447a-8aa9-4a8c27ceeba4",
                            "order": 4,
                            "title": "Operating expense",
                            "remark": "Operating expense",
                            "syntax": "indicator(Operating expense)",
                            "example": "indicator(Operating expense)",
                            "syntax_show": "indicator(Operating expense)",
                            "formula_data": [
                                {
                                    "id": "aebaf647-49ff-4d59-a738-41ed6a583b50",
                                    "code": "sumItemIf",
                                    "title": "sumItemIf",
                                    "remark": "Returns total of items that pass condition.",
                                    "syntax": "sumItemIf(",
                                    "example": "sumItemIf((5, 2, 9, 3), '>3') == 14",
                                    "param_type": 2,
                                    "syntax_show": "sumItemIf(item_check_list, condition, item_sum_list)",
                                    "function_data": [
                                        {
                                            "id": "8ecc50e2-e7d6-4b0d-9cd5-92eec83f8f95",
                                            "code": "expense_type_title",
                                            "type": 1,
                                            "title": "Expense type",
                                            "remark": "Type expense on quotation expense line",
                                            "syntax": "prop(Expense type)",
                                            "properties": {

                                            },
                                            "is_property": True,
                                            "syntax_show": "prop(Expense type)",
                                            "content_type": None
                                        },
                                        "===",
                                        "chiphítriểnkhai",
                                        {
                                            "id": "f0251c13-0480-4ac1-94d3-ebe03afb93bf",
                                            "code": "expense_subtotal_price",
                                            "type": 6,
                                            "title": "Expense subtotal before tax",
                                            "remark": "Subtotal before tax expense on quotation expense line",
                                            "syntax": "prop(Expense subtotal before tax)",
                                            "properties": {},
                                            "is_property": True,
                                            "syntax_show": "prop(Expense subtotal before tax)",
                                            "content_type": None
                                        }
                                    ]
                                }
                            ],
                            "is_indicator": True,
                            "formula_data_show":
                                'sumItemIf(prop(Expense type)=="Chi phí triển khai",prop(Expense subtotal before tax))'
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show": "prop(Total expense before tax) - indicator(Operating expense)"
                }
            ],
            "formula_data_show": "indicator(Gross profit) - indicator(Operating expense) - indicator(Other expenses)",
            "order": 6
        }
    ]
