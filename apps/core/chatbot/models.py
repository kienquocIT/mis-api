# from django.db import models
# from django.utils import timezone
#
# from apps.shared import SimpleAbstractModel
#
#
# class Chatbot(SimpleAbstractModel):
#     tenant = models.ForeignKey(
#         'tenant.Tenant', on_delete=models.CASCADE,
#         related_name='%(app_label)s_%(class)s_belong_to_tenant',
#     )
#     company = models.ForeignKey(
#         'company.Company', on_delete=models.CASCADE,
#         related_name='%(app_label)s_%(class)s_belong_to_company',
#     )
#     employee_inherit = models.ForeignKey(
#         'hr.Employee', on_delete=models.CASCADE,
#         related_name='%(app_label)s_%(class)s_employee_inherit',
#     )
#
#     class Meta:
#         verbose_name = 'Chatbot'
#         verbose_name_plural = 'Chatbot'
#         default_permissions = ()
#         permissions = ()
#
#
# class ChatbotHistory(SimpleAbstractModel):
#     tenant = models.ForeignKey(
#         'tenant.Tenant', on_delete=models.CASCADE,
#         related_name='%(app_label)s_%(class)s_belong_to_tenant',
#     )
#     company = models.ForeignKey(
#         'company.Company', on_delete=models.CASCADE,
#         related_name='%(app_label)s_%(class)s_belong_to_company',
#     )
#     employee_inherit = models.ForeignKey(
#         'hr.Employee', on_delete=models.CASCADE,
#         related_name='%(app_label)s_%(class)s_employee_inherit',
#     )
#     date_created = models.DateTimeField(
#         default=timezone.now, editable=False,
#         help_text='The record created at value',
#     )
#     date_modified = models.DateTimeField(
#         auto_now=True,
#         help_text='Date modified this record in last',
#     )
#
#     question = models.TextField()
#     answer = models.TextField(null=True)
#
#     class Meta:
#         verbose_name = 'Chatbot History'
#         verbose_name_plural = 'Chatbot History'
#         ordering = ('-date_created',)
#         default_permissions = ()
#         permissions = ()
