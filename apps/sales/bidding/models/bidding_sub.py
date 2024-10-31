from rest_framework import serializers
from apps.core.base.models import Application
from apps.sales.bidding.models import BiddingAttachment, BiddingDocument, BiddingPartnerAccount
from apps.shared.translations.base import AttachmentMsg

class BiddingCommonCreate:
    @classmethod
    def handle_attach_file( cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.filter(id="ad1e1c4e-2a7e-4b98-977f-88d069554657").first()
            if relate_app:
                state = BiddingAttachment.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
        return True

    @classmethod
    def create_sub_models( cls, instance, create_data):

        if create_data['document_data']:
            cls.create_document(document_data=create_data['document_data'], instance=instance, attachment_result =create_data['attachment'])
        if create_data['venture_partner']:
            cls.create_venture_partner(venture_partner=create_data['venture_partner'], instance=instance)
        return True

    @classmethod
    def create_venture_partner(cls,venture_partner, instance):
        venture_instance_list = BiddingPartnerAccount.objects.filter_current(bidding=instance).all()
        if venture_instance_list:
            venture_instance_list.delete()
        bulk_data = []
        for item in venture_partner:
            bulk_data.append(
                BiddingPartnerAccount(
                    bidding=instance,
                    partner_account=item['partner_account'],
                    is_leader=item['is_leader']
                )
            )
        BiddingPartnerAccount.objects.bulk_create(bulk_data)

    @classmethod
    def create_document( cls,document_data, instance, attachment_result):
        bidding_doc_instance_list = BiddingDocument.objects.filter_current(bidding=instance).all()
        if bidding_doc_instance_list:
            bidding_doc_instance_list.delete()
        cls.handle_attach_file(instance=instance, attachment_result=attachment_result)
        bulk_data = []
        for item in document_data:
            bulk_data.append(
                BiddingDocument(
                    bidding=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                    **item
                )
            )
        bidding_doc_instance_list = BiddingDocument.objects.bulk_create(bulk_data)
        for bidding_doc_instance in bidding_doc_instance_list:
            for item in bidding_doc_instance.attachment_data:
                bidding_attach_instance = BiddingAttachment.objects.filter_current(
                    attachment_id=item.get('attachment').get('id') if item.get('attachment') else None,
                    bidding_id=instance.id
                ).first()
                if bidding_attach_instance:
                    bidding_attach_instance.document = bidding_doc_instance
                    bidding_attach_instance.save(update_fields=['document'])