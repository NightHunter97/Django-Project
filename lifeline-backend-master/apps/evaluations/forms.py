from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group
from django.forms import ModelMultipleChoiceField, ModelForm
from django.utils.translation import ugettext_lazy as _

from apps.evaluations.models import Survey, Question


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = (
            'survey', 'question',  'question_fr', 'question_nl'
        )


class AddGroupSurveyForm(ModelForm):
    groups = ModelMultipleChoiceField(
        label=_('Survey'), queryset=Group.objects.all(), widget=FilteredSelectMultiple('Group', is_stacked=True),
        required=False
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.setdefault('initial', {})
            initial['groups'] = [group.pk for group in instance.groups.all()]
        super().__init__(*args, **kwargs)

    class Meta:
        model = Survey
        fields = (
            'name_en', 'name_fr', 'name_nl', 'groups'
        )

    def save(self, commit=True):
        instance = super().save(False)
        _save_m2m = self.save_m2m

        def save_m2m():
            _save_m2m()
            instance.groups.clear()
            instance.groups.add(*self.cleaned_data['groups'])
        self.save_m2m = save_m2m
        if commit:
            instance.save()
            self.save_m2m()
        return instance
