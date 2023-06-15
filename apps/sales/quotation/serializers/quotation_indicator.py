# from rest_framework import serializers
#
# from apps.sales.quotation.models import Indicator
#
#
# # class IndicatorFormulaSerializer(serializers.ModelSerializer):
# #
# #     class Meta:
# #         model = IndicatorFormula
# #         fields = (
# #             'is_indicator_param',
# #             'is_sale_param',
# #             'is_math_operator',
# #             'indicator_param',
# #             'sale_param',
# #             'math_operator',
# #             'order',
# #         )
#
#
# class IndicatorListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Indicator
#         fields = (
#             'id',
#             'title',
#             'description',
#             'order',
#         )
#
#
# class IndicatorDetailSerializer(serializers.ModelSerializer):
#     indicator_formula = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Indicator
#         fields = (
#             'id',
#             'title',
#             'description',
#             'order',
#             'indicator_formula'
#         )
#
#     @classmethod
#     def get_indicator_formula(cls, obj):
#         if obj:
#             return {}
#         return {}
#
#
# # Quotation
# class IndicatorCreateSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Indicator
#         fields = (
#             'title',
#             'description',
#             'order',
#         )
#
#     def create(self, validated_data):
#         indicator = Indicator.objects.create(**validated_data)
#         return indicator
#
#
# class IndicatorUpdateSerializer(serializers.ModelSerializer):
#     # indicator_formula = IndicatorFormulaSerializer(
#     #     many=True,
#     #     required=False
#     # )
#
#     class Meta:
#         model = Indicator
#         fields = (
#             'title',
#             'description',
#             # 'indicator_formula',
#             'order',
#         )
#
#     def update(self, instance, validated_data):
#         for key, value in validated_data.items():
#             setattr(instance, key, value)
#         instance.save()
#         return instance
