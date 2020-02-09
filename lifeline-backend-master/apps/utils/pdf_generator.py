from django.core.cache import cache
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


class PDFBaseGenerator:
    """Generates pdf file and put the pdf data into cache"""
    template_path = None

    def __init__(self, prefix, object_id, owner):
        """
        :param prefix: cache prefix for specific file
        :param object_id: primary key for specific object
        """
        self.object_id = object_id
        self.owner = owner
        self.cache_key = f'export_pdf_{prefix}_{object_id}'

    def proceed(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="export.pdf"'
        template = get_template(self.template_path)
        cache.set(self.cache_key, 'generating', None)
        html = template.render(self.get_context())
        pisa.CreatePDF(html, dest=response, encoding='UTF-8')
        cache.set(self.cache_key, {
            'content': response.content,
            'owner': self.owner,
        }, 300)

    @classmethod
    def get_context(cls):
        """Get prepared context for pdf template"""
        raise NotImplementedError
