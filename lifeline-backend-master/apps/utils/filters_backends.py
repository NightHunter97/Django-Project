from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class StrictSearchFilter(BaseFilterBackend):
    search_result_limit = 50

    def filter_queryset(self, request, queryset, *args, **kwargs):
        search = request.query_params.get('search')
        if not search:
            return queryset.none()
        starts = list(queryset.filter(Q(term__istartswith=search)))
        rest = list(queryset.exclude(Q(term__istartswith=search)))
        return (starts + rest)[0:self.search_result_limit]
