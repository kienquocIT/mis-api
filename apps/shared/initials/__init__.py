from .data.plan import plan_data, application_data, plan_application_data
from .data.property import APPLICATION_PROPERTY_DATA
from .data.workflow import NODE_SYSTEM_DATA
from ..models import DisperseModel


class Initial:
    def __init__(self):
        pass

    def run(self):
        self.create_plan()
        self.create_application()
        self.create_plan_application()
        self.create_system_node()
        self.create_application_property()
        return True

    @classmethod
    def create_plan(cls):
        # plan
        plan_model = DisperseModel(app_model='base_SubscriptionPlan').get_model()
        plan_check = plan_model.objects.all()
        if plan_check:
            plan_check.delete()
        records = plan_model.objects.bulk_create(
            [plan_model.__class__(**tmp) for tmp in plan_data]
        )
        return records

    @classmethod
    def create_application(cls):
        # application
        application_model = DisperseModel(app_model='base_Application').get_model()
        application_check = application_model.objects.all()
        if application_check:
            application_check.delete()
        records = application_model.objects.bulk_create(
            [application_model.__class__(**tmp) for tmp in application_data]
        )  # pylint: disable=E1102
        return records

    @classmethod
    def create_plan_application(cls):
        # plan application
        plan_application_model = DisperseModel(app_model='base_PlanApplication').get_model()
        plan_application_check = plan_application_model.objects.all()
        if plan_application_check:
            plan_application_check.delete()
        records = plan_application_model.objects.bulk_create(
            [plan_application_model.__class__(**tmp) for tmp in plan_application_data]
        )
        return records

    @classmethod
    def create_system_node(cls):
        node_model = DisperseModel(app_model='workflow_Node').get_model()
        node_check = node_model.objects.filter(
            is_system=True,
            tenant_id=None,
            company_id=None
        )
        if node_check:
            node_check.delete()
        node = node_model.objects.bulk_create(NODE_SYSTEM_DATA)
        print('create system node successfully.')
        return node

    @classmethod
    def create_application_property(cls):
        property_model = DisperseModel(app_model='base_ApplicationProperty').get_model()
        property_check = property_model.objects.all()
        if property_check:
            property_check.delete()
        app_property = property_model.objects.bulk_create(APPLICATION_PROPERTY_DATA)
        print('create application property successfully.')
        return app_property
