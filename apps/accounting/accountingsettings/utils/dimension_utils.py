import logging

from django.apps import apps
# from django.db import transaction
# from django.utils import timezone

from apps.accounting.accountingsettings.models import Dimension, DimensionValue, DimensionSyncConfig
from apps.shared import DisperseModel

logger = logging.getLogger(__name__)


class DimensionUtils:

    @staticmethod
    def sync_dimension_value(instance, app_id, title, code):
        application = DimensionUtils._get_application(app_id=app_id)
        mapped_dimension = Dimension.objects.filter(related_app=application).first()
        sync_config = DimensionSyncConfig.objects.filter(dimension=mapped_dimension).first()
        if not application or not mapped_dimension or not sync_config:
            return True
        if not mapped_dimension or not sync_config.sync_on_save:
            return True

        # # find existing mapping
        # existing_value = DimensionValue.objects.filter(
        #     related_app=application,
        #     related_doc_id=instance.id,
        #     dimension=mapped_dimension
        # ).first()
        #
        # if is_create or not existing_value:
        #     #  Create new
        #     DimensionValue.objects.create(
        #         title=title,
        #         code=code,
        #         dimension=mapped_dimension,
        #         parent=None,
        #         allow_posting=True,
        #         related_app=application,
        #         related_doc_id=instance.id,
        #     )
        # else:
        #     #  Update existing mapping
        #     existing_value.title = title
        #     existing_value.code = code
        #     existing_value.save()

        obj, _created = DimensionValue.objects.get_or_create(
            tenant_id=instance.tenant_id, company_id=instance.company_id,
            related_app=application, related_doc_id=instance.id, dimension=mapped_dimension,
            defaults={
                'title': title,
                'code': code,
                'allow_posting': True,
                'date_created': instance.date_created,
            }
        )
        # create new record
        if _created is True:
            return True
        # update old record
        obj.title = title
        obj.code = code
        obj.save(update_fields=['title', 'code'])

        return True

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
        # dimension_values_to_create = []

        field_mapping = model_class.get_field_mapping()
        code_field = field_mapping.get('code')
        title_field = field_mapping.get('title')

        if not code_field or not title_field:
            logger.error("%s.get_field_mapping() missing 'code' or 'title'", model_class.__name__)
            return False

        # for record in existing_records:
        #     code_value = getattr(record, code_field, None)
        #     title_value = getattr(record, title_field, None)
        #
        #     dimension_value = DimensionValue(
        #         code=code_value,
        #         title=title_value,
        #         tenant_id=record.tenant_id,
        #         company_id=record.company_id,
        #         date_created=timezone.now(),
        #
        #         dimension=dimension,
        #         related_app=application,
        #         related_doc_id=record.id,
        #         allow_posting=True,
        #         parent=None
        #     )
        #     dimension_values_to_create.append(dimension_value)
        #
        # if dimension_values_to_create:
        #     with transaction.atomic():
        #         DimensionValue.objects.bulk_create(
        #             dimension_values_to_create
        #         )

        for record in existing_records:
            DimensionUtils.sync_dimension_value(  # dimension
                instance=record,
                app_id=record.__class__.get_app_id(),
                title=getattr(record, title_field, None),
                code=getattr(record, code_field, None),
            )

        return True

    # @staticmethod
    # def auto_delete_dimension_value(instance, app_id):
    #     ...

    @classmethod
    def _get_application(cls, app_id):
        model_app = DisperseModel(app_model='base.application').get_model()
        if model_app and hasattr(model_app, 'objects'):
            return model_app.objects.filter(id=app_id).first()
        return None
