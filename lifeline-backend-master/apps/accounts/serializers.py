import jwt
from django.utils.translation import ugettext_lazy as _
from rest_auth.serializers import PasswordResetSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_jwt.utils import jwt_encode_handler
from django.contrib.auth import get_user_model
from jwt import ExpiredSignatureError, DecodeError, InvalidAlgorithmError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.authentication import JSONWebTokenAuthentication, jwt_decode_handler
from rest_framework_jwt.serializers import jwt_encode_handler
from rest_framework_jwt.utils import jwt_payload_handler

from apps.accounts.models import User


class AccountResetSerializer(PasswordResetSerializer):

    def get_email_options(self):
        return {
            'subject_template_name': 'accounts/password_reset_subject.txt',
            'email_template_name': 'accounts/password_reset_email.html'
        }


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'pk')


class UserDetailsSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'language')
        read_only_fields = ('email', 'pk', 'username',)


class RefreshJwtSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, token):
        if self._check_payload(token) is True:
            return token
        refresh_token = JSONWebTokenAuthentication().get_jwt_value(self.context['request'])
        try:
            payload = jwt_decode_handler(refresh_token)
            if 'refresh' not in payload:
                raise AuthenticationFailed(_('Token type is wrong.'))
            user = get_user_model().objects.get(uuid=payload['uuid'])
        except (AuthenticationFailed,
                get_user_model().DoesNotExist,
                InvalidAlgorithmError,
                ExpiredSignatureError,
                DecodeError) as ex:
            raise AuthenticationFailed(ex)
        return jwt_encode_handler(jwt_payload_handler(user))

    @staticmethod
    def _check_payload(token):
        try:
            jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            return token
        except (jwt.DecodeError, jwt.InvalidAlgorithmError):
            msg = _('Error decoding signature.')
            raise serializers.ValidationError(msg)
        return True
