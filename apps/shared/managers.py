from django.db import models

__all__ = [
    'NormalManager'
]


class NormalManager(models.Manager):
    def get_queryset(self):  # pylint: disable=W0246
        return super().get_queryset()
