from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.core.account.models import TOTPUser, User


@receiver(post_save, sender=TOTPUser)
def change_totp_user(sender, instance, created, **kwargs):
    # if instance.confirmed is True and instance.user and instance.user.auth_2fa is False:
    #     instance.user.auth_2fa = True
    #     instance.user.save(update_fields=['auth_2fa'])
    pass


@receiver(post_delete, sender=TOTPUser)
def delete_totp_user(sender, instance, **kwargs):
    if instance.confirmed is True and instance.user_id:
        user_obj = User.objects.get(pk=instance.user_id)
        if user_obj.auth_2fa is True:
            instance.user.auth_2fa = False
            instance.user.save(update_fields=['auth_2fa'])
