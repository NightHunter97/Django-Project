import os

from django import forms

from apps.documents.models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('author', 'name', 'file', 'patient_file', 'document_type')

    def clean(self, *args, **kwargs):
        data = self.cleaned_data
        content = data.get('file', None)
        if content is None or content == "":
            raise forms.ValidationError("Content is required")
        else:
            file = data.get('file', None)
            _, extension = os.path.splitext(file.name)
        if extension not in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.rtf']:
            raise forms.ValidationError("File is required, expected format: pdf, doc, docx, xls, xlsx, rtf")
        return super().clean(*args, **kwargs)
