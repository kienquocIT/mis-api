from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel, SimpleAbstractModel

TYPE_CUSTOMER = [
    (0, _('Direct Customer')),
    (1, _('End Customer')),
]

CONTACT_ROLE = [
    (0, _('Decision maker')),
    (1, _('Influence')),
    (2, _('Contact involved')),
]


class Opportunity(DataAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="opportunity_customer",
        null=True
    )

    sale_person = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="sale person",
        related_name='opportunity_sale_person',
        null=True,
    )

    end_customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="end customer buy from customer",
        related_name="opportunity_end_customer",
        null=True
    )

    product_category = models.ManyToManyField(
        'saledata.ProductCategory',
        through="OpportunityProductCategory",
        symmetrical=False,
        blank=True,
        default=None,
        related_name='product_category_map_opportunity',
    )
    budget_value = models.FloatField(
        verbose_name="expected budget",
        default=0,
    )

    open_date = models.DateTimeField(
        help_text='Opportunity open at value',
        null=True,
        default=None,
    )

    close_date = models.DateTimeField(
        help_text='Opportunity close at value',
        null=True,
        default=None,
    )

    decision_maker = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        related_name="opportunity_decision_maker",
        null=True,
        default=None,
    )

    opportunity_product_datas = models.JSONField(
        default=list,
        help_text="read data product, use for get list or detail opportunity"
    )

    total_product_pretax_amount = models.FloatField(
        default=0,
        help_text="total pretax amount of tab product"
    )

    total_product_tax = models.FloatField(
        default=0,
        help_text="total tax of tab product"
    )
    total_product = models.FloatField(
        default=0,
        help_text="total amount of tab product"
    )

    opportunity_competitors_datas = models.JSONField(
        default=list,
        help_text="read data competitors, use for get list or detail opportunity"
    )

    opportunity_contact_role_datas = models.JSONField(
        default=list,
        help_text="read data contact role, use for get list or detail opportunity"
    )

    win_rate = models.FloatField(
        default=0,
        help_text='possibility of win deal of opportunity'
    )

    is_input_rate = models.BooleanField(
        default=False,
    )

    customer_decision_factor = models.ManyToManyField(
        'opportunity.CustomerDecisionFactor',
        through="OpportunityCustomerDecisionFactor",
        symmetrical=False,
        verbose_name='reason why customer buy product',
        blank=True,
        default=None,
        related_name='decision_factor_map_opportunity',
    )

    class Meta:
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        opportunity = Opportunity.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "OPP.CODE."
        if not self.code:
            temper = "%04d" % (opportunity + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code

        # hit DB
        super().save(*args, **kwargs)


class OpportunityProductCategory(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_product_category_opportunity",
    )

    product_category = models.ForeignKey(
        'saledata.ProductCategory',
        on_delete=models.CASCADE,
        related_name="opportunity_product_category_product_category",
    )

    class Meta:
        verbose_name = 'OpportunityProductCategory'
        verbose_name_plural = 'OpportunitiesProductsCategory'
        ordering = ()
        default_permissions = ()
        permissions = ()


class OpportunityProduct(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_product_opportunity",
    )

    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="opportunity_product_product",
        null=True
    )

    product_category = models.ForeignKey(
        'saledata.ProductCategory',
        on_delete=models.CASCADE,
        related_name="opportunity_product_product_category",
        null=True
    )

    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name="opportunity_product_uom",
        null=True
    )

    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        related_name="opportunity_product_tax",
        null=True
    )

    product_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    product_quantity = models.FloatField(
        default=0
    )
    product_unit_price = models.FloatField(
        default=0
    )
    product_subtotal_price = models.FloatField(
        default=0
    )

    class Meta:
        verbose_name = 'Opportunity Product Category'
        verbose_name_plural = 'Opportunity Products Category'
        ordering = ()
        default_permissions = ()
        permissions = ()


class OpportunityCompetitor(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_competitor_opportunity",
    )

    competitor = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="competitor with customer",
        related_name="opportunity_competitor_competitor",
        null=True
    )

    strength = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    weakness = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    win_deal = models.BooleanField(
        default=False,
        verbose_name='customer is win deal'
    )

    class Meta:
        verbose_name = 'Opportunity Competitor'
        verbose_name_plural = 'Opportunity Competitors'
        ordering = ()
        default_permissions = ()
        permissions = ()


class OpportunityContactRole(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_contact_role_opportunity",
    )

    type_customer = models.SmallIntegerField(
        choices=TYPE_CUSTOMER,
        help_text='0 is Direct, 1 is End',
        default=0
    )

    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name='Contact of customer or end customer',
        related_name="opportunity_contact_role_contact",
        null=True
    )

    job_title = models.CharField(
        default='',
        max_length=100,
        verbose_name='job title of contact'
    )

    role = models.SmallIntegerField(
        choices=CONTACT_ROLE,
        help_text='0 is Direct, 1 is End',
        default=0
    )

    class Meta:
        verbose_name = 'Opportunity Contact Role'
        verbose_name_plural = 'Opportunity Contacts Role'
        ordering = ()
        default_permissions = ()
        permissions = ()


class OpportunityCustomerDecisionFactor(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_customer_decision_factor_opportunity",
    )

    factor = models.ForeignKey(
        'opportunity.CustomerDecisionFactor',
        on_delete=models.CASCADE,
        verbose_name='reason why customer buy product',
        related_query_name='opportunity_customer_decision_factor_factor',
    )

    class Meta:
        verbose_name = 'Opportunity Contact Role'
        verbose_name_plural = 'Opportunity Contacts Role'
        ordering = ()
        default_permissions = ()
        permissions = ()
