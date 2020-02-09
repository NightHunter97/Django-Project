from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelMultipleChoiceField, ModelForm
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import User
from apps.units.services import get_all_units


class UserAddForm(UserCreationForm):
    groups = ModelMultipleChoiceField(label=_('Role'), queryset=Group.objects.all())
    units = ModelMultipleChoiceField(label=_('Unit'), queryset=get_all_units())
    last_name = CharField(required=True)


class UserUpdateForm(UserChangeForm):
    groups = ModelMultipleChoiceField(label=_('Role'), queryset=Group.objects.all())


class UserAddPermissionForm(ModelForm):
    users = ModelMultipleChoiceField(
        label=_('User'), queryset=User.objects.all(), widget=FilteredSelectMultiple('Users', is_stacked=True),
        required=False
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.setdefault('initial', {})
            initial['users'] = [user.pk for user in instance.user_set.all()]
        super().__init__(*args, **kwargs)

    class Meta:
        model = Group
        fields = ('name', 'permissions',)

    def clean_users(self):
        selected_users = self.cleaned_data['users']
        if self.instance.id:
            for user in self.instance.user_set.all():
                if user not in selected_users and user.groups.count() == 1:
                    raise ValidationError(f'{user}: should have at least 1 role', code='invalid')
        return selected_users

    def save(self, commit=True):
        instance = super().save(False)
        _save_m2m = self.save_m2m

        def save_m2m():
            _save_m2m()
            instance.user_set.clear()
            instance.user_set.add(*self.cleaned_data['users'])
        self.save_m2m = save_m2m
        if commit:
            instance.save()
            self.save_m2m()
        return instance
