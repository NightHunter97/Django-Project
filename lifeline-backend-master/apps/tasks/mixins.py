from django.conf import settings


class LocalStaticServe:
    @staticmethod
    def _is_local():
        return settings.TRANSFER_PROTOCOL == 'http'

    def _get_local_static_file(self, url):
        request = self._kwargs['context']['request']
        return f'{settings.TRANSFER_PROTOCOL}://{request.META["HTTP_HOST"]}{url}'
