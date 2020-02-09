import requests
from django.conf import settings
from rest_framework.response import Response


class BrusafeGetDataMixin:
    def post(self, request):
        response = requests.get(
            f'https:{settings.BRUSAFE_HOST}/{self.endpoint_url}', params=request.data, headers=self.api_headers
        )
        return Response({'detail': response.content}, status=response.status_code)


class BrusafePutDataMixin:
    def post(self, request):
        response = requests.put(
            f'https:{settings.BRUSAFE_HOST}/{self.endpoint_url}', data=request.data, headers=self.api_headers
        )
        return Response({'detail': response.content}, status=response.status_code)
