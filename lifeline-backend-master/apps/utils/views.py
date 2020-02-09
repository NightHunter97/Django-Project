from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from xhtml2pdf import pisa
from urllib.parse import quote


class BaseExportView(APIView):
    """
    Base view for export.
    """
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        return self.get_pdf_file(request)

    @classmethod
    def _get_context(cls, request):
        raise NotImplementedError

    def get_pdf_file(self, request):
        response = HttpResponse(content_type='application/pdf')
        try:
            name = quote(self.get_export_name(request))
        except TypeError:
            name = self.get_export_name(request)
        response['Content-Disposition'] = f'attachment; filename="export {name}.pdf"'
        template = get_template(self.template_path)
        html = template.render(self._get_context(request))
        pisa.CreatePDF(html, dest=response, encoding='UTF-8')
        return response

    @classmethod
    def get_export_name(cls, request):
        raise NotImplementedError
