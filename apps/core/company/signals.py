from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.company.models import Company


@receiver(post_save, sender=Company)
def update_company(sender, instance, created, **kwargs):
    if instance.tenant:
        instance.tenant.company_total = Company.objects.filter(tenant=instance.tenant).count()
        instance.tenant.save()
