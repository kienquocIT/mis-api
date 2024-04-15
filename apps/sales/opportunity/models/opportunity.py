import json
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.company.models import CompanyFunctionNumber
from apps.core.hr.models import PermissionAbstractModel
from apps.shared import (
    DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel
)
from .config import OpportunityConfigStage, OpportunityConfig

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

    opportunity_sale_team_datas = models.JSONField(
        default=list,
        help_text="read data sale team member, use for get list or detail opportunity"
    )
    quotation = models.OneToOneField(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        null=True,
        help_text="quotation use this opportunity",
        related_name="opportunity_map_quotation"
    )
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        null=True,
        help_text="sale order use this opportunity",
        related_name="opportunity_map_sale_order"
    )

    stage = models.ManyToManyField(
        'opportunity.OpportunityConfigStage',
        through="OpportunityStage",
        symmetrical=False,
        blank=True,
        related_name='opportunity_map_stage'
    )

    lost_by_other_reason = models.BooleanField(
        default=False,
    )

    is_close_lost = models.BooleanField(
        default=False
    )

    is_deal_close = models.BooleanField(
        default=False
    )

    delivery = models.OneToOneField(
        'delivery.OrderDelivery',
        on_delete=models.CASCADE,
        null=True,
        help_text="Delivery use this opportunity",
        related_name="opportunity_map_delivery"
    )
    members = models.ManyToManyField(
        'hr.Employee',
        through='OpportunitySaleTeamMember',
        symmetrical=False,
        through_fields=('opportunity', 'member'),
        blank=True,
        related_name='member_of_opp'
    )
    estimated_gross_profit_percent = models.FloatField(
        default=0
    )
    estimated_gross_profit_value = models.FloatField(
        default=0
    )

    class Meta:
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def common_check_property_stage(cls, obj):
        list_property = []

        # customer
        customer_data = {
            'condition_property': {
                'id': 'e4e0c770-a0d1-492d-beae-3b31dcb391e1',
                'title': 'Customer'
            },
            'comparison_operator': '≠' if obj.customer else '=',
            'compare_data': 0,
        }
        list_property.append(customer_data)

        if obj.customer:
            customer_data = {
                'condition_property': {
                    'id': 'e4e0c770-a0d1-492d-beae-3b31dcb391e1',
                    'title': 'Customer'
                },
                'comparison_operator': '=',
                'compare_data': obj.customer.annual_revenue,
            }
            list_property.append(customer_data)

        # Product category
        list_property.append(
            {
                'condition_property': {
                    'id': '496aca60-bf3d-4879-a4cb-6eb1ebaf4ce8',
                    'title': 'Product Category'
                },
                'comparison_operator': '≠' if len(obj.product_category.all()) > 0 else '=',
                'compare_data': 0,
            }
        )

        # Budget
        list_property.append(
            {
                'condition_property': {
                    'id': '36233e9a-8dc9-4a7c-a6ad-504bac91d4cb',
                    'title': 'Budget'
                },
                'comparison_operator': '=' if obj.budget_value == 0 else '≠',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': '195440c2-41bc-43f1-b387-fc5cd26401df',
                    'title': 'Open Date'
                },
                'comparison_operator': '≠' if obj.open_date else '=',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': '43009b1a-a25d-43be-ab97-47540a2f00cb',
                    'title': 'Close Date'
                },
                'comparison_operator': '≠' if obj.close_date else '=',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': '35dbf6f2-78a8-4286-8cf3-b95de5c78873',
                    'title': 'Decision maker'
                },
                'comparison_operator': '≠' if obj.decision_maker else '=',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': '92c8035a-5372-41c1-9a8e-4b048d8af406',
                    'title': 'Lost By Other Reason'
                },
                'comparison_operator': '=' if obj.lost_by_other_reason else '≠',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': 'c8fa79ae-2490-4286-af25-3407e129fedb',
                    'title': 'Competitor.Win'
                },
                'comparison_operator': '=' if not obj.lost_by_other_reason and obj.is_close_lost else '≠',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': '39b50254-e32d-473b-8380-f3b7765af434',
                    'title': 'Product.Line.Detail'
                },
                'comparison_operator': '≠' if len(obj.opportunity_product_datas) > 0 else '=',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': 'f436053d-f15a-4505-b368-9ccdf5afb5f6',
                    'title': 'Close Deal'
                },
                'comparison_operator': '=' if obj.is_deal_close else '≠',
                'compare_data': 0,
            }
        )
        return list_property

    @classmethod
    def check_property_stage_when_saving_quotation(cls, obj, is_quotation_confirm):
        list_property = cls.common_check_property_stage(obj)

        list_property.append(
            {
                'condition_property': {
                    'id': 'acab2c1e-74f2-421b-8838-7aa55c217f72',
                    'title': 'Quotation.confirm'
                },
                'comparison_operator': '=' if is_quotation_confirm else '≠',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': '9db4e835-c647-4de5-aa1c-43304ddeccd1',
                    'title': 'SaleOrder.status'
                },
                'comparison_operator': '=' if obj.sale_order and obj.sale_order.system_status == 0 else '≠',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': 'b5aa8550-7fc5-4cb8-a952-b6904b2599e5',
                    'title': 'SaleOrder.Delivery.Status'
                },
                'comparison_operator': '≠' if obj.sale_order and obj.sale_order.delivery_call else '=',
                'compare_data': 0,
            }
        )
        return list_property

    @classmethod
    def check_property_stage_when_saving_sale_order(cls, obj, sale_order_status):
        list_property = cls.common_check_property_stage(obj)

        list_property.append(
            {
                'condition_property': {
                    'id': '9db4e835-c647-4de5-aa1c-43304ddeccd1',
                    'title': 'SaleOrder.status'
                },
                'comparison_operator': '≠' if sale_order_status == 0 else '=',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': 'acab2c1e-74f2-421b-8838-7aa55c217f72',
                    'title': 'Quotation.confirm'
                },
                'comparison_operator':
                    '=' if obj.quotation and obj.quotation.system_status == 0 and obj.quotation.is_customer_confirm
                    else '≠',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': 'b5aa8550-7fc5-4cb8-a952-b6904b2599e5',
                    'title': 'SaleOrder.Delivery.Status'
                },
                'comparison_operator': '≠' if obj.sale_order and obj.sale_order.delivery_call else '=',
                'compare_data': 0,
            }
        )
        return list_property

    @classmethod
    def check_property_stage_when_saving_delivery(cls, obj, delivery_status):
        list_property = cls.common_check_property_stage(obj)

        list_property.append(
            {
                'condition_property': {
                    'id': '9db4e835-c647-4de5-aa1c-43304ddeccd1',
                    'title': 'SaleOrder.status'
                },
                'comparison_operator': '=',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': 'b5aa8550-7fc5-4cb8-a952-b6904b2599e5',
                    'title': 'SaleOrder.Delivery.Status'
                },
                'comparison_operator': '≠' if delivery_status else '=',
                'compare_data': 0,
            }
        )

        list_property.append(
            {
                'condition_property': {
                    'id': 'acab2c1e-74f2-421b-8838-7aa55c217f72',
                    'title': 'Quotation.confirm'
                },
                'comparison_operator': '='
                if obj.quotation and obj.quotation.system_status == 0 and obj.quotation.is_customer_confirm
                else '≠',
                'compare_data': 0,
            }
        )
        return list_property

    @classmethod
    def auto_update_stage(cls, list_property, obj):
        stages = OpportunityConfigStage.objects.filter(company_id=obj.company_id).order_by('win_rate')

        stage_lost = None
        stage_delivery = None
        stage_close = None

        list_stage = []
        # sort stage [stage 1, stage 2, ...., stage Close Lost, stage Delivery, stage Deal Close
        for item in stages:
            if item.is_closed_lost:
                stage_lost = item
            elif item.is_deal_closed:
                stage_close = item
            elif item.is_delivery:
                stage_delivery = item
            else:
                list_stage.append(item)

        if stage_lost:
            list_stage.append(stage_lost)

        if stage_delivery:
            list_stage.append(stage_delivery)

        if stage_close:
            list_stage.append(stage_close)

        # check stage
        index = 0
        win_rate = 0
        for idx, item in enumerate(list_stage):
            if item.logical_operator == 0:
                if all(element in list_property for element in item.condition_datas):
                    index = idx
                    win_rate = item.win_rate
            else:
                if any(element in list_property for element in item.condition_datas):
                    index = idx
                    win_rate = item.win_rate
        bulk_data = [
            OpportunityStage(
                opportunity=obj,
                stage_id=item.id,
                is_current=False
            ) for item in list_stage[:index + 1]]
        bulk_data[-1].is_current = True
        obj.stage.clear()
        OpportunityStage.objects.bulk_create(bulk_data)
        return win_rate

    @classmethod
    def check_config_auto_update_stage(cls):
        config = OpportunityConfig.objects.filter_current(fill__company=True).first()
        if config.is_select_stage:
            return False
        return True

    def save(self, *args, **kwargs):
        if not self.code:
            code_generated = CompanyFunctionNumber.gen_code(company_obj=self.company, func=0)
            if code_generated:
                self.code = code_generated
            else:
                records = Opportunity.objects.filter_current(fill__tenant=True, fill__company=True, is_delete=False)
                self.code = 'OPP.00' + str(records.count() + 1)

        keys_condition = ('quotation_confirm', 'sale_order_status', 'delivery_status')
        if any(key in kwargs for key in keys_condition) and not self.is_close_lost and not self.is_deal_close:
            if 'quotation_confirm' in kwargs:
                if self.check_config_auto_update_stage():
                    self.win_rate = self.auto_update_stage(
                        self.check_property_stage_when_saving_quotation(self, kwargs['quotation_confirm']),
                        self
                    )
                del kwargs['quotation_confirm']
            elif 'sale_order_status' in kwargs:
                if self.check_config_auto_update_stage():
                    self.win_rate = self.auto_update_stage(
                        self.check_property_stage_when_saving_sale_order(self, kwargs['sale_order_status']),
                        self
                    )
                del kwargs['sale_order_status']
            elif 'delivery_status' in kwargs:
                if self.check_config_auto_update_stage():
                    self.win_rate = self.auto_update_stage(
                        self.check_property_stage_when_saving_delivery(self, kwargs['delivery_status']),
                        self
                    )
                del kwargs['delivery_status']
            if 'update_fields' in kwargs:
                kwargs['update_fields'].append('win_rate')
            else:
                kwargs.update({'update_fields': ['win_rate']})
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
        related_name='opportunity_customer_decision_factor_factor',
    )

    class Meta:
        verbose_name = 'Opportunity Customer Decision Factor'
        verbose_name_plural = 'Opportunity Customer Decision Factors'
        ordering = ()
        default_permissions = ()
        permissions = ()


class OpportunitySaleTeamMember(MasterDataAbstractModel, PermissionAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_sale_team_member_opportunity",
    )
    member = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name='Member of Sale Team of Opportunity',
        related_name='opportunity_sale_team_member_member',
    )
    date_modified = models.DateTimeField(
        help_text='Date modified this record in last',
        default=timezone.now,
    )

    permit_view_this_opp = models.BooleanField(
        default=False,
        verbose_name='member can view this Opportunity'
    )
    permit_add_member = models.BooleanField(
        default=False,
        verbose_name='member can add other member but can not set permission for member'
    )
    permit_app = models.JSONField(
        default=dict,
        help_text=json.dumps(
            {
                'app_id': {
                    'is_create': False,
                    'is_edit': False,
                    'is_view': False,
                    'is_delete': False,
                    'all': False,
                    'belong_to': 0  # 0: user , 1: opportunity member
                }
            }
        ),
        verbose_name='permission for member in Tenant App'
    )
    plan = models.ManyToManyField(
        'base.SubscriptionPlan',
        through="PlanMemberOpportunity",
        through_fields=('opportunity_member', 'plan'),
        symmetrical=False,
        blank=True,
        related_name='member_opp_map_plan'
    )

    def get_app_allowed(self) -> str:
        return str(self.member_id)

    def sync_parsed_to_main(self):
        ...

    class Meta:
        verbose_name = 'Opportunity Sale Team Member'
        verbose_name_plural = 'Opportunity Sale Team Members'
        ordering = ()
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant', 'company', 'opportunity', 'member')


class PlanMemberOpportunity(SimpleAbstractModel):
    opportunity_member = models.ForeignKey(
        OpportunitySaleTeamMember,
        on_delete=models.CASCADE,
        related_name='member_opp_plan'
    )
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE
    )
    application = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Plan of Employee At Opportunity'
        verbose_name_plural = 'Plan of Employee At Opportunity'
        default_permissions = ()
        permissions = ()


class OpportunityStage(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_stage_opportunity",
    )

    stage = models.ForeignKey(
        'opportunity.OpportunityConfigStage',
        on_delete=models.CASCADE,
        related_name="opportunity_stage_stage",
        null=True,
        default=None,
    )

    is_current = models.BooleanField(
        default=False,
    )

    class Meta:
        verbose_name = 'Opportunity Stage'
        verbose_name_plural = 'Opportunity Stages'
        ordering = ()
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if str(self.opportunity.company_id) != str(self.stage.company_id):
            raise ValueError('Can not update opp stage because of different company between opp & stage config')
        super().save(*args, **kwargs)
