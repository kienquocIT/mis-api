import logging

from django.apps import apps
from django.db import transaction
from django.utils import timezone

from apps.accounting.accountingsettings.models import Dimension, DimensionValue
from apps.core.base.models import Application

logger = logging.getLogger(__name__)

class DimensionUtils:
    @staticmethod
    def auto_create_dimension_value(instance, app_id, title, code):
        application = Application.objects.get(id=app_id)

        mapped_dimension = Dimension.objects.get(related_app=application)

        if mapped_dimension and mapped_dimension.sync_on_create:
            DimensionValue.objects.create(
                title=title,
                code=code,
                dimension=mapped_dimension,
                parent=None,
                allow_posting=True,
                related_app=application,
                relate_doc_id=instance.id,
            )

    @staticmethod
    def sync_old_data(dimension_config):
        application = dimension_config.related_app
        dimension = dimension_config.dimension

        try:
            model_class = apps.get_model(application.app_label, application.model_code)
        except LookupError:
            logger.error(msg='Sync old data for dimension error: Cannot find model class')
            return False

        existing_records = model_class.objects.filter_on_company()
        dimension_values_to_create = []

        field_mapping = model_class.get_field_mapping()
        code_field = field_mapping.get('code')
        title_field = field_mapping.get('title')

        if not code_field or not title_field:
            logger.error(f"{model_class.__name__}.get_field_mapping() missing 'code' or 'title'")
            return False

        for record in existing_records:
            code_value = getattr(record, code_field, None)
            title_value = getattr(record, title_field, None)

            dimension_value = DimensionValue(
                code=code_value,
                title=title_value,
                tenant_id=record.tenant_id,
                company_id=record.company_id,
                date_created=timezone.now(),

                dimension=dimension,
                related_app=application,
                relate_doc_id=record.id,
                allow_posting=True,
                parent=None
            )
            dimension_values_to_create.append(dimension_value)

        if dimension_values_to_create:
            with transaction.atomic():
                DimensionValue.objects.bulk_create(
                    dimension_values_to_create
                )

        return True

    @staticmethod
    def auto_delete_dimension_value(instance, app_id, title, code):
        ...