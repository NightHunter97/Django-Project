import datetime

from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.urls import resolve
from rest_framework_jwt.utils import jwt_encode_handler

from apps.accounts.serializers import UserDetailsSerializer
from apps.evaluations.services import get_enabled_surveys_for_user_groups
from apps.tasks.services import get_categories_for_user_groups
from django.conf import settings


def jwt_refresh_payload_handler(user):
    return {
        'uuid': str(user.pk),
        'refresh': True,
        'exp': datetime.datetime.utcnow() + settings.JWT_AUTH['JWT_REFRESH_TOKEN_EXPIRATION_DELTA']
    }


def get_categories_permissions(user):
    """
    Returns permissions for each category
    :param user:
    :return set: set of available categories
    """
    categories_perms = set(get_categories_for_user_groups(user).values_list('slug', flat=True))
    if not categories_perms or categories_perms == {'medication'}:
        categories_perms = categories_perms | {'no_categories'}
    return categories_perms


def get_survey_permissions(user):
    """
    Returns permissions for each survey
    :param user:
    :return set: set of available surveys
    """
    return set(get_enabled_surveys_for_user_groups(user).values_list('name', flat=True))


def get_main_permissions(perms, user):
    """
    Returns main apps permissions
    :param perms: permissions
    :param user: user
    :return: all permissions if superuser, else groups permissions
    """
    return set(perms.values_list('codename', flat=True)) \
        if user.is_superuser else set(perms.filter(group__user=user).values_list('codename', flat=True))


def jwt_response_payload_handler(token, user=None, request=None):
    """
    :param token: jwt token
    :param user:
    :param request:
    :return dict:
    """
    url_name = resolve(request.path_info).url_name
    perms = Permission.objects.all()
    return {
        'token': token,
        'refresh_token': jwt_encode_handler(jwt_refresh_payload_handler(user)) if url_name == 'login' else None,
        'brusafe_token': cache.get(f'{user.uuid}_brusafe'),
        'user': UserDetailsSerializer(user).data,
        'permissions': get_survey_permissions(user) | get_categories_permissions(user)
        | get_main_permissions(perms, user),
        'is_superuser': user.is_superuser,
    }
