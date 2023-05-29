from typing import Union

from django.db import models

from apps.shared import DisperseModel

APP_CODE_MAP_MODELS = {
    '': ''
}

__all__ = ['DocHandler']


class DocHandler:
    @property
    def model(self) -> models.Model:
        model_cls = DisperseModel(app_model=self.app_code).get_model()
        if model_cls and hasattr(model_cls, 'objects'):
            return model_cls
        raise ValueError('App code is incorrect. Value: ' + self.app_code)

    def __init__(self, doc_id, app_code):
        self.doc_id = doc_id
        self.app_code = app_code

    def get_obj(self, default_filter: dict) -> Union[models.Model, None]:
        try:
            return self.model.objects.get(pk=self.doc_id, **default_filter)
        except self.model.DoesNotExist:
            return None
