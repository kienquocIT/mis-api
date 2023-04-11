from rest_framework import serializers

from apps.sales.quotation.models.quotation import Quotation, QuotationProduct


class QuotationProductSerializer(serializers.ModelSerializer):
    product = serializers.CharField(
        max_length=550
    )
    unit_of_measure = serializers.CharField(
        max_length=550
    )
    tax = serializers.CharField(
        max_length=550
    )

    class Meta:
        model = QuotationProduct
        fields = (
            'product',
            'unit_of_measure',
            'tax',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_uom_title',
            'product_uom_code',
            'product_quantity',
            'product_unit_price',
            'product_tax_title',
            'product_tax_value',
            'product_subtotal_price',
            'order',
        )


class QuotationInformationSerializer(serializers.Serializer): # noqa
    quotation_product = ...
    quotation_term = ...
    quotation_logistic = ...
    quotation_cost = ...
    quotation_expense = ...


# Quotation
class QuotationCreateSerializer(serializers.ModelSerializer):
    information = QuotationInformationSerializer(required=False)

    class Meta:
        model = Quotation
        fields = (
            'title',
            'opportunity',
            'customer',
            'contact',
            'sale_person',
            'information',
            'total_pretax_revenue',
            'total_tax',
            'total',
            'is_customer_confirm'
        )