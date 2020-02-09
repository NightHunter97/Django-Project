import jwt
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.views import RefreshJSONWebToken, VerifyJSONWebToken

from apps.accounts.serializers import RefreshJwtSerializer


class RefreshJwtView(RefreshJSONWebToken):
    serializer_class = RefreshJwtSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if request.data['token'] == serializer.data['token']:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class VerifyJwt(VerifyJSONWebToken):
    def post(self, request, *args, **kwargs):
        try:
            jwt_decode_handler(request.data['token'])
        except jwt.ExpiredSignature:
            return Response({'token': _('Signature has expired.')}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.DecodeError, jwt.InvalidAlgorithmError):
            pass
        return super().post(request, *args, **kwargs)
