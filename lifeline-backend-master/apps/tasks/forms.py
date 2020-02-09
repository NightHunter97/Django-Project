from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group
from django.forms import ModelMultipleChoiceField, ModelForm
from django.utils.translation import ugettext_lazy as _

from apps.tasks.models import Task


class AddGroupCategoryForm(ModelForm):
    groups = ModelMultipleChoiceField(
        label=_('Category'),
        queryset=Group.objects.all(),
        widget=FilteredSelectMultiple('Group', is_stacked=True),
        required=False
    )

    class Meta:
        model = Group
        fields = ('groups',)

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


class TaskForm(ModelForm):

    class Meta:
        model = Task
        fields = (
            'name_en',
            'name_fr',
            'name_nl',
            'category'
        )
