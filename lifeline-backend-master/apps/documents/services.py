from django.db.models import Q

from apps.documents.models import DocumentType, Document

def get_all_document_types():
   return DocumentType.objects.all()

def get_all_documents():
   return Document.objects.all()
