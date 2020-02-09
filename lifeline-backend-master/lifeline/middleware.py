import json
import re

import pytz

from django.middleware.locale import LocaleMiddleware
from django.utils import translation, timezone
from django.utils.deprecation import MiddlewareMixin

from apps.accounts.tasks import user_activity_track
from apps.reports.activities_mapping import ACTIVITIES


class LifeLineLocaleMiddleware(LocaleMiddleware):
    def process_request(self, request):
        language = request.META.get('HTTP_LANGUAGE')
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()
        else:
            super().process_request(request)

    def process_response(self, request, response):
        response["Pragma"] = "no-cache"
        return super().process_response(request, response)


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.META.get('HTTP_TZINFO')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


class UserActivityMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        # @TODO we need to define how importnant this structure is, because it's breaks APIClient tests
        try:
            activities = [activity for activity in ACTIVITIES if re.match(activity['path'], request.scope.get('path'))
                          and activity['method'] == request.scope['method']]
            if activities:
                activity = activities[0]
                if activity['code'] == response.status_code:
                    user_activity_track.delay(
                        request.user.username,
                        request.user.email,
                        activity['info'],
                        request.scope['path'].split('/')[activity['file_index']] or
                        json.loads(request.body).get(activity['file_data']) if request.body else None,
                        response.data.get('patient_id') if isinstance(response.data, dict) else None,
                        data=self._prepare_data(request.body)
                    )
            return response
        except:
            return response

    @staticmethod
    def _prepare_data(body):
        if not body:
            return None
        try:
            return re.sub('[{}]', '', body.decode('utf-8').replace(',', ', '))
        except UnicodeDecodeError:
            return None
