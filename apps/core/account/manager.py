from django.db import models
from django.contrib.auth.base_user import BaseUserManager

from apps.shared import DisperseModel


class AccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, phone, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email) if email else None
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self, username, phone=None, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, phone, email, password, **extra_fields)

    def create_superuser(self, username_auth, password, email, phone=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        tenant = self.get_virtual_tenant_admin()
        if tenant:
            obj = self._create_user(username_auth, phone, email, password, tenant_current=tenant, **extra_fields)
            obj.save(is_superuser=True)
            return obj
        return self._create_user(username_auth, phone, email, password, **extra_fields)

    @staticmethod
    def get_virtual_tenant_admin():
        model_cls = DisperseModel(app_model='tenant_tenant').get_model()
        if model_cls:
            obj, _created = model_cls.objects.get_or_create(
                id='073ed4a2-53fd-4a37-abd8-e5e176b97fe2',
                defaults={
                    'title': 'ADMIN',
                    'code': 'ADMIN',
                    'sub_domain': 'ADMIN',
                    'representative_fullname': 'Virtual-Tenant-Admin',
                    'representative_phone_number': 'Virtual-Tenant-Admin',
                }
            )
            return obj
        return None

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class GroupManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)
