from datetime import datetime, date

from django.conf import settings


class FORMATTING:
    DATETIME = settings.REST_FRAMEWORK['DATETIME_FORMAT']
    DATE = settings.REST_FRAMEWORK['DATE_FORMAT']
    PAGE_SIZE = settings.REST_FRAMEWORK['PAGE_SIZE']

    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, datetime):
            return datetime.strftime(value, cls.DATETIME) if value else None
        return str(value)

    @classmethod
    def parse_date(cls, value):
        if isinstance(value, date):
            return datetime.strftime(value, cls.DATE) if value else None
        return str(value)
