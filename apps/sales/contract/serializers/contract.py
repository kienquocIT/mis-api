# from rest_framework import serializers
#
# # from apps.core.workflow.tasks import decorator_run_workflow
# from apps.sales.contract.models import Contract
# from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel
#
#
# # CONTRACT BEGIN
# class ContractListSerializer(AbstractListSerializerModel):
#
#     class Meta:
#         model = Contract
#         fields = (
#             'id',
#             'title',
#             'code',
#         )
#
#
# class ContractDetailSerializer(AbstractDetailSerializerModel):
#     opportunity = serializers.SerializerMethodField()
#     customer = serializers.SerializerMethodField()
#     contact = serializers.SerializerMethodField()
#     sale_person = serializers.SerializerMethodField()
#     employee_inherit = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Contract
#         fields = (
#             'id',
#             'title',
#             'code',
#             'employee_inherit',
#         )
#
#
# class ContractCreateSerializer(AbstractCreateSerializerModel):
#     title = serializers.CharField()
#     employee_inherit_id = serializers.UUIDField()
#
#     class Meta:
#         model = Contract
#         fields = (
#             'title',
#             'employee_inherit_id',
#         )
#
#     # @decorator_run_workflow
#     def create(self, validated_data):
#         contract = Contract.objects.create(**validated_data)
#         return contract
#
#
# class ContractUpdateSerializer(AbstractCreateSerializerModel):
#     employee_inherit_id = serializers.UUIDField(
#         required=False,
#         allow_null=True,
#     )
#
#     class Meta:
#         model = Contract
#         fields = (
#             'title',
#             'employee_inherit_id',
#         )
#
#     # @decorator_run_workflow
#     def update(self, instance, validated_data):
#         # update quotation
#         for key, value in validated_data.items():
#             setattr(instance, key, value)
#         instance.save()
#         return instance
