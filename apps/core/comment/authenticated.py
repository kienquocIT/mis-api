__all__ = ['VerifyPermit']

from django.apps import apps

from apps.shared.extends.utils import TypeCheck
from apps.shared.extends.mask_view import ViewAttribute, ViewConfigDecorator, ViewChecking


def get_view_decor_feature(app_obj):
    default_kwargs = {'employee_require': True, 'perm_code': 'view'}

    if app_obj.app_label == 'task':
        if app_obj.model_code == 'OpportunityTask'.lower():
            return {'label_code': 'task', 'model_code': 'OpportunityTask'.lower(), **default_kwargs}
    return {'label_code': app_obj.app_label.lower(), 'model_code': app_obj.model_code.lower(), **default_kwargs}


class VerifyPermit:
    @property
    def model_application(self):
        return apps.get_model(app_label='base', model_name='application')

    def setup(self, application_id):
        try:
            if not application_id:
                raise self.model_application.DoesNotExist
            self.app_obj = self.model_application.objects.get(pk=application_id)
            self.model_cls = apps.get_model(app_label=self.app_obj.app_label, model_name=self.app_obj.model_code)
        except self.model_application.DoesNotExist:
            raise ValueError('[VerifyPermit] Application is not found.')

    def __init__(self, application_id):
        [self.app_obj, self.model_cls] = [None, None]
        self.setup(application_id)

    def verify(self, idx, view_self, decor_check: dict = None) -> bool:
        decor_check = decor_check if decor_check else get_view_decor_feature(app_obj=self.app_obj)

        try:
            obj = self.model_cls.objects.get(pk=idx)
        except self.model_cls.DoesNotExist:
            return False

        _cls_attr = ViewAttribute(view_this=view_self)
        _cls_decor = ViewConfigDecorator(parent_kwargs=decor_check)
        cls_check = ViewChecking(cls_attr=_cls_attr, cls_decor=_cls_decor)

        opportunity_id = getattr(obj, 'opportunity', None)
        project_id = getattr(obj, 'project', None)
        employee_inherit_id = getattr(obj, 'employee_inherit', None)

        if project_id and opportunity_id:
            return False

        if employee_inherit_id and TypeCheck.check_uuid(employee_inherit_id):
            check_kwargs = {'employee_inherit_id': employee_inherit_id}

            if opportunity_id and TypeCheck.check_uuid(opportunity_id):
                check_on_id = cls_check.permit_cls.config_data__check_obj_on_id_list(obj=obj)
                if check_on_id is True:
                    return True
                return cls_check.permit_cls.config_data__check_by_opp(opp_id=opportunity_id, **check_kwargs)

            if project_id and TypeCheck.check_uuid(project_id):
                return cls_check.permit_cls.config_data__check_by_prj(prj_id=project_id, **check_kwargs)

        return cls_check.permit_cls.config_data__check_obj(obj=obj)
