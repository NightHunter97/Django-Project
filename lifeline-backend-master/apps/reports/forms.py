from django import forms

from apps.reports.models import Report
from django.utils.translation import ugettext_lazy as _


class LogoForm(forms.ModelForm):
    MAX_LOGO_SIZE = 100000

    class Meta:
        model = Report
        fields = '__all__'

    def clean_image(self):
        image = self.cleaned_data['image']
        if image.size > self.MAX_LOGO_SIZE:
            raise forms.ValidationError(_('Logo size should be less than 100kB'))
        return image
