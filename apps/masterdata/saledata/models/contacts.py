from django.db import models
from apps.shared import DataAbstractModel, MasterDataAbstractModel

__all__ = [
    'Salutation',
    'Interest',
    'Contact',
]

# Contact Master data
class Salutation(MasterDataAbstractModel):  # noqa
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'Salutation'
        verbose_name_plural = 'Salutations'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()


class Interest(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()


# Contact
class Contact(DataAbstractModel):
    owner = models.ForeignKey(
        'hr.Employee',
        verbose_name='Contact owner mapped',
        on_delete=models.CASCADE,
        null=True
    )
    biography = models.CharField(
        blank=True,
        null=True,
        max_length=150
    )
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )
    fullname = models.CharField(
        verbose_name='contact fullname',
        null=False,
        max_length=150
    )
    salutation = models.ForeignKey(
        'saledata.Salutation',
        on_delete=models.CASCADE,
        null=True
    )
    phone = models.CharField(
        verbose_name='contact phone number',
        blank=True,
        null=True,
        max_length=25
    )
    mobile = models.CharField(
        verbose_name='contact mobile',
        blank=True,
        null=True,
        max_length=25
    )
    account_name = models.ForeignKey(
        'saledata.Account',
        verbose_name='account name',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contact_account_name'
    )
    email = models.CharField(
        verbose_name='contact email',
        blank=True,
        null=True,
        max_length=150
    )
    job_title = models.CharField(
        verbose_name='contact job title',
        blank=True,
        null=True,
        max_length=150
    )
    report_to = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='report to another contact'
    )

    # {
    #   "work_address": "Số 2/8, Xã Định An, Huyện Dầu Tiếng, Bình Dương",
    #   "home_address": "Số 22/20, Phường Lê Hồng Phong, Thành Phố Phủ Lý, Hà Nam"
    # }
    address_information = models.JSONField(
        default=dict,
    )

    # {
    #   'facebook': 'nva.facebook.com',
    #   'twitter': 'nva.twitter.com',
    #   'linkedln': 'nva.linkedln.com',
    #   'gmail': 'nva@gmail.com',
    #   'interests': ["e3e416d7-ae74-4bb8-a55f-169c5fde53a0", "d2f9397d-3a6c-46d6-9a67-442bc43554a8"],
    #   'tags': 'tags',
    # }
    additional_information = models.JSONField(
        default=dict,
    )
    is_primary = models.BooleanField(
        help_text='is account owner',
        default=False
    )

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
