"""
# [django-storage[s3]]
#   Documentations:
#       https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
#       https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
#   Sample:
#       https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/
#       https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html
"""

from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage
from django.conf import settings


class BastionStorageLocal(FileSystemStorage):
    def url(self, name, parameters=None, expire=None, http_method=None):
        # expire: seconds
        return super().url(name=name)


class StaticStorage(BastionStorageLocal):
    """
    Storage for static files (everyone allow READ, owner allow FULL CONTROL)
    """
    ...


class PublicMediaStorage(BastionStorageLocal):
    """
    Storage for public file (everyone allow READ, owner allow FULL CONTROL)
    """
    ...


class PrivateMediaStorage(BastionStorageLocal):
    """
    Storage for private file (nobody allow READ, owner allow FULL CONTROL)

    Rule return Url of File (link expires: settings.AWS_QUERYSTRING_EXPIRE)
    Valid by DATA of API --> valid current user allow view document related to attachment object.
        Allow: return file.url -> full link access preview
        Deny: None
    """
    ...


if settings.USE_S3 is True:
    """
    Change class to extend from S3Boto3Storage when site using S3 (settings.S3 is True)
    MUST fill data to key in environment (or fill in .env - same level with manage.py):
        USE_S3=1
        AWS_ACCESS_KEY_ID={ACCESS_KEY}
        AWS_SECRET_ACCESS_KEY={SECRET_ACCESS_KEY}
        AWS_STORAGE_BUCKET_NAME={BUCKET_NAME}
        AWS_S3_REGION_NAME={REGION_OF_BUCKET}
    """

    class StaticStorage(S3Boto3Storage):  # noqa
        """
        Override some data S3 for Static Files
            location: static push to folder settings.STATIC_LOCATION | 'static'
            default_acl: allow everyone READ
        """
        location = settings.STATIC_LOCATION
        default_acl = 'public-read'


    class PublicMediaStorage(S3Boto3Storage):  # noqa
        """
        Override some data s3 for Public Files
            location: public file push to folder settings.STATIC_LOCATION | 'media/public'
            default_acl: allow everyone READ
            file_overwrite: don't allow override exist files (append random string to end when duplicate)
        """
        location = settings.PUBLIC_MEDIA_LOCATION
        default_acl = 'public-read'
        file_overwrite = False


    class PrivateMediaStorage(S3Boto3Storage):  # noqa
        """
        Override some data s3 for Private Files
            location: private file push to folder settings.PRIVATE_MEDIA_LOCATION | 'media/private'
            default_acl: nobody allow READ exclude owner
            file_overwrite: don't allow override exist files (append random string to end when duplicate)
            custom_domain: not using settings.AWS_S3_CUSTOM_DOMAIN -> use domain default boto3 provide.
        """
        location = settings.PRIVATE_MEDIA_LOCATION
        default_acl = 'private'
        file_overwrite = False
        custom_domain = False
