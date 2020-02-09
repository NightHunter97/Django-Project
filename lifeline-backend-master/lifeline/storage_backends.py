from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class PrivateMediaStorage(S3Boto3Storage):
    location = settings.AWS_STORAGE_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False


class PublicStaticStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_STATIC_LOCATION
