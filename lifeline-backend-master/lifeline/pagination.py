from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class Pagination(PageNumberPagination):

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pages', (self.page.paginator.count - 1) // self.page_size + 1),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
