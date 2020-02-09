import datetime
import json
import time
import requests

from django.conf import settings
from apps.brusafe.models import Connector


class BrusafeConnector:
    auth_url = 'auth/realms/abrumet/protocol/openid-connect/auth/'
    token_url = 'auth/realms/abrumet/protocol/openid-connect/token'

    def connect(self, code, request):
        connector = Connector(user=request.user)
        self.flush_session(request)
        payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.BRUSAFE_CLIENT_ID,
            'client_secret': settings.BRUSAFE_CLIENT_SECRET,
            'code': code
        }
        response = requests.post(f'https:{settings.BRUSAFE_HOST}/{self.token_url}', payload)
        content = json.loads(response.content)
        if response.status_code != 200:
            connector.authenticated = True
            expiration = datetime.datetime.now() + datetime.timedelta(seconds=int(content['expires_in']))
            connector.expiration = expiration
            request.session['brusafe_expiration_in'] = time.mktime(expiration.timetuple())
            request.session['brusafe_token'] = content['access_token']
        else:
            request.session['brusafe_error'] = content['error']
            request.session['brusafe_error_description'] = content['error_description']
        connector.save()

    @staticmethod
    def flush_session(request):
        request.session.pop('brusafe_token', None)
        request.session.pop('brusafe_error', None)
        request.session.pop('brusafe_error_description', None)
        request.session.pop('brusafe_expiration_in', None)

    @staticmethod
    def is_session_token_expired(request):
        expiration = datetime.datetime.fromtimestamp(request.session.get('brusafe_expiration_in', 0))
        brusafe_token = request.session.get('brusafe_token')
        return brusafe_token and expiration < datetime.datetime.now()

    @staticmethod
    def is_session_token_set(request):
        return request.session.get('brusafe_token')
