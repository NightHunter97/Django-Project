from rest_framework import filters

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import LifeLinePermissions
from apps.journal.filter_backends import FileJournalFilter
from apps.journal.serializers import JournalSerializer
from apps.journal.services import get_journal_notes
from apps.journal import choices


class JournalViewSet(ModelViewSet):
    queryset = get_journal_notes()
    serializer_class = JournalSerializer
    filter_backends = (filters.SearchFilter, FileJournalFilter)
    search_fields = ('name',)
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    http_method_names = ['get', 'post', 'head', 'options', 'patch']


class JournalMetaView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        data = {
            'tags': [{'key': item[0], 'value': item[1]} for item in choices.JOURNAL_TAG_TYPE],
            'types': [{'key': item[0], 'value': item[1]} for item in choices.JOURNAL_COMMENT_TYPE]
        }
        return Response(data, status=status.HTTP_200_OK)
