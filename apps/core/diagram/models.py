from django.db import models

from apps.shared import MasterDataAbstractModel


class DiagramDocument(MasterDataAbstractModel):
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    doc_id = models.UUIDField(verbose_name='Main document show diagram')
    doc_data = models.JSONField(default=dict)

    @classmethod
    def push_diagram_document(
            cls,
            tenant_id,
            company_id,
            app_code,
            doc_id,
            doc_data,
    ):
        obj, _created = cls.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, app_code=app_code, doc_id=doc_id,
            defaults={
                'doc_data': doc_data,
            }
        )
        if _created is True:  # create new record
            return True
        obj.doc_data = doc_data
        obj.save(update_fields=['doc_data'])
        return True

    class Meta:
        verbose_name = 'Diagram Document'
        verbose_name_plural = 'Diagram Documents'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()


class DiagramPrefix(MasterDataAbstractModel):
    diagram_doc = models.ForeignKey(
        DiagramDocument,
        on_delete=models.CASCADE,
        verbose_name="Diagram document",
        related_name="diagram_prefix_diagram_document",
    )
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    doc_id = models.UUIDField(verbose_name='Related document to main document')
    doc_data = models.JSONField(default=dict)

    @classmethod
    def push_diagram_prefix(
            cls,
            tenant_id,
            company_id,
            app_code_main,
            doc_id_main,
            app_code,
            doc_id,
            doc_data,
    ):
        diagram_doc = DiagramDocument.objects.filter(app_code=app_code_main, doc_id=doc_id_main).first()
        if diagram_doc:
            obj, _created = cls.objects.get_or_create(
                tenant_id=tenant_id, company_id=company_id, app_code=app_code,
                doc_id=doc_id, diagram_doc_id=diagram_doc.id,
                defaults={
                    'doc_data': doc_data,
                }
            )
            if _created is True:  # create new record
                return True
            obj.doc_data = doc_data
            obj.save(update_fields=['doc_data'])
        return True

    class Meta:
        verbose_name = 'Diagram Prefix'
        verbose_name_plural = 'Diagram Prefixes'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class DiagramSuffix(MasterDataAbstractModel):
    diagram_doc = models.ForeignKey(
        DiagramDocument,
        on_delete=models.CASCADE,
        verbose_name="Diagram document",
        related_name="diagram_suffix_diagram_document",
    )
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    doc_id = models.UUIDField(verbose_name='Related document to main document')
    doc_data = models.JSONField(default=dict)

    @classmethod
    def push_diagram_suffix(
            cls,
            tenant_id,
            company_id,
            app_code_main,
            doc_id_main,
            app_code,
            doc_id,
            doc_data,
    ):
        diagram_doc = DiagramDocument.objects.filter(app_code=app_code_main, doc_id=doc_id_main).first()
        if diagram_doc:
            obj, _created = cls.objects.get_or_create(
                tenant_id=tenant_id, company_id=company_id, app_code=app_code,
                doc_id=doc_id, diagram_doc_id=diagram_doc.id,
                defaults={
                    'doc_data': doc_data,
                }
            )
            if _created is True:  # create new record
                return True
            obj.doc_data = doc_data
            obj.save(update_fields=['doc_data'])
        return True

    class Meta:
        verbose_name = 'Diagram Suffix'
        verbose_name_plural = 'Diagram Suffixes'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
