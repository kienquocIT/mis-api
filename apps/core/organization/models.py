# from django.db import models
#
# from apps.shared import TenantCoreModel
#
#
# # Organization Group Level
# class GroupLevel(TenantCoreModel):
#     level = models.IntegerField(
#         verbose_name='group level',
#         null=True
#     )
#     description = models.CharField(
#         verbose_name='group level description',
#         max_length=500,
#         blank=True,
#         null=True
#     )
#     first_manager_description = models.CharField(
#         verbose_name='first manager description',
#         max_length=500,
#         blank=True,
#         null=True
#     )
#     second_manager_description = models.CharField(
#         verbose_name='second manager description',
#         max_length=500,
#         blank=True,
#         null=True
#     )
#
#     class Meta:
#         verbose_name = 'Group Level'
#         verbose_name_plural = 'Group Levels'
#         ordering = ('-date_created',)
#         default_permissions = ()
#         permissions = ()
#
#
# # Organization group
# class Group(TenantCoreModel):
#     group_level = models.ForeignKey(
#         'organization.GroupLevel',
#         on_delete=models.CASCADE,
#         null=True
#     )
#     parent_n = models.ForeignKey(
#         "self",
#         on_delete=models.CASCADE,
#         related_name="group_parent_n",
#         verbose_name="parent group",
#         null=True,
#     )
#     description = models.CharField(
#         verbose_name='group description',
#         max_length=600,
#         blank=True,
#         null=True
#     )
#     first_manager = models.ForeignKey(
#         'hr.Employee',
#         on_delete=models.CASCADE,
#         null=True
#     )
#     first_manager_title = models.CharField(
#         verbose_name='first manager title',
#         max_length=100,
#         blank=True,
#         null=True
#     )
#
#     class Meta:
#         verbose_name = 'Group'
#         verbose_name_plural = 'Groups'
#         ordering = ('-date_created',)
#         default_permissions = ()
#         permissions = ()
