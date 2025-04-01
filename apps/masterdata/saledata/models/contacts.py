from django.db import models
from apps.shared import DataAbstractModel, MasterDataAbstractModel

__all__ = [
    'Salutation',
    'Interest',
    'Contact',
]

# Contact Master data
class Salutation(MasterDataAbstractModel):  # noqa
    code = models.CharField(max_length=100)
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Salutation'
        verbose_name_plural = 'Salutations'
        ordering = ('code',)
        unique_together = ('company', 'code')
        default_permissions = ()
        permissions = ()


class Interest(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

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
    biography = models.TextField(blank=True, null=True)
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
        related_name='contact_account_name'
    )
    email = models.TextField(
        verbose_name='contact email',
        blank=True,
        null=True,
    )
    job_title = models.TextField(
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
    #   'interests': [{'id', 'code', 'title'}, ...],
    #   'tags': 'tags',
    # }
    additional_information = models.JSONField(
        default=dict,
    )
    is_primary = models.BooleanField(
        help_text='is account owner',
        default=False
    )

    # home address fields
    home_country = models.ForeignKey(
        'base.Country',
        on_delete=models.CASCADE,
        null=True,
        related_name='home_country'
    )
    home_detail_address = models.TextField(
        verbose_name='Detail home address',
        blank=True,
        null=True,
    )
    home_city = models.ForeignKey(
        'base.City',
        on_delete=models.CASCADE,
        null=True,
        related_name='home_city'
    )
    home_district = models.ForeignKey(
        'base.District',
        on_delete=models.CASCADE,
        null=True,
        related_name='home_district'
    )
    home_ward = models.ForeignKey(
        'base.Ward',
        on_delete=models.CASCADE,
        null=True,
        related_name='home_ward'
    )
    home_address_data = models.JSONField(
        default=dict,
    )

    # work address fields
    work_country = models.ForeignKey(
        'base.Country',
        on_delete=models.CASCADE,
        null=True,
        related_name='work_country'
    )
    work_detail_address = models.TextField(
        verbose_name='Detail work address',
        blank=True,
        null=True,
    )
    work_city = models.ForeignKey(
        'base.City',
        on_delete=models.CASCADE,
        null=True,
        related_name='work_city'
    )
    work_district = models.ForeignKey(
        'base.District',
        on_delete=models.CASCADE,
        null=True,
        related_name='work_district'
    )
    work_ward = models.ForeignKey(
        'base.Ward',
        on_delete=models.CASCADE,
        null=True,
        related_name='work_ward'
    )
    work_address_data = models.JSONField(
        default=dict,
    )

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ('-date_created',)
        unique_together = ('company', 'code')
        default_permissions = ()
        permissions = ()
