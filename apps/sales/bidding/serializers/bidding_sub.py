from rest_framework import serializers
from apps.core.base.models import Application
from apps.sales.bidding.models import BiddingAttachment, BiddingDocument, BiddingPartnerAccount, BiddingBidderAccount
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
        if create_data.get('document_data'):
            cls.create_document(document_data=create_data.get('document_data'), instance=instance,
                                attachment_result=create_data.get('attachment'))
        if create_data.get('venture_partner'):
            cls.create_venture_partner(venture_partner=create_data.get('venture_partner'), instance=instance)
        return True

    @classmethod
    def create_venture_partner(cls,venture_partner, instance):
        bulk_data = []
        for item in venture_partner:
            bulk_data.append(
                BiddingPartnerAccount(
                    bidding=instance,
                    order=item.get('order'),
                    partner_account=item.get('partner_account'),
                    is_leader=item.get('is_leader')
                )
            )
        BiddingPartnerAccount.objects.filter(bidding=instance).delete()
        BiddingPartnerAccount.objects.bulk_create(bulk_data)

    @classmethod
    def create_other_bidder(cls, other_bidder, instance):
        bulk_data = []
        for item in other_bidder:
            bulk_data.append(
                BiddingBidderAccount(
                    bidding=instance,
                    order=item.get('order'),
                    bidder_account=item.get('bidder_account'),
                    is_won=item.get('is_won')
                )
            )
        BiddingBidderAccount.objects.filter(bidding=instance).delete()
        BiddingBidderAccount.objects.bulk_create(bulk_data)

    @classmethod
    def create_document( cls,document_data, instance, attachment_result):
        bulk_data = []
        for item in document_data:
            bulk_data.append(
                BiddingDocument(
                    bidding=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                    **item
                )
            )
        BiddingDocument.objects.filter(bidding=instance).delete()
        cls.handle_attach_file(instance=instance, attachment_result=attachment_result)
        bidding_doc_instance_list = BiddingDocument.objects.bulk_create(bulk_data)
        for bidding_doc_instance in bidding_doc_instance_list:
            for item in bidding_doc_instance.attachment_data:
                bidding_attach_instance = BiddingAttachment.objects.filter_current(
                    attachment_id=item.get('attachment').get('id') if item.get('attachment') else None,
                    bidding=instance
                ).first()
                if bidding_attach_instance:
                    bidding_attach_instance.document = bidding_doc_instance
                    bidding_attach_instance.save(update_fields=['document'])
