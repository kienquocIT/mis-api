import pytz
from django.conf import settings

from django.db import models

from apps.shared import SimpleAbstractModel

__all__ = [
    'MailServerConfig',
]


class MailServerConfig(SimpleAbstractModel):
    token_data = models.JSONField()

    token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.TextField()
    client_id = models.TextField()
    client_secret = models.TextField()
    scopes = models.JSONField()
    expiry = models.DateTimeField()

    @property
    def tokens(self):
        return {
            "token": self.token,
            "refresh_token": self.refresh_token,
            "token_uri": self.token_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scopes": self.scopes,
            "expiry": pytz.timezone(settings.TIME_ZONE).localize(self.expiry).strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
        }

    def __str__(self):
        return self.client_id

    class Meta:
        verbose_name = 'Mail Server Config'
        verbose_name_plural = 'Mail Server Config'
        ordering = ('-expiry',)
        default_permissions = ()
        permissions = ()
