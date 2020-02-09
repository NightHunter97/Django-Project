from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import AdminActivity

from django.utils.encoding import force_text
from django.utils.translation import (
    override as translation_override,
)


class AdminLogMixin:
    def log_addition(self, request, object, message):
        log_entry = super().log_addition(request, object, message)
        self.create_admin_log(log_entry, object)
        return log_entry

    def log_change(self, request, object, message):
        log_entry = super().log_change(request, object, message)
        self.create_admin_log(log_entry, object)
        return log_entry

    def log_deletion(self, request, object, object_repr):
        log_entry = super().log_deletion(request, object, object_repr)
        self.create_admin_log(log_entry, object)
        return log_entry

    @staticmethod
    def create_admin_log(log_entry, object):
        file = getattr(object, 'file', None)
        patient = getattr(object, 'patient', None)
        patient_id = getattr(object, 'patient_id', None)
        if file:
            AdminActivity.objects.create(log_entry=log_entry, patient_id=file.patient.pk)
        elif patient:
            AdminActivity.objects.create(log_entry=log_entry, patient_id=patient.pk)
        elif patient_id:
            AdminActivity.objects.create(log_entry=log_entry, patient_id=object.pk)

    def construct_change_message(self, request, form, formsets, add=False):
        """
        Construct a JSON structure describing changes from a changed object.
        Translations are deactivated so that strings are stored untranslated.
        Translation happens later on LogEntry access.
        """
        change_message = []
        if add:
            change_message.append(
                str(_('Added with fields') + ': ' + ', '.join(
                    [f'{field.replace("_", " ")}: {form.cleaned_data.get(field) or " - "}'
                     for field in form.changed_data]))
            )
        elif form.changed_data:
            change_message.append(
                str(_('Changed with fields') + ': ' + ', '.join(
                 [f'{field.replace("_", " ")}:' + str(_(" from '")) + f'{form.initial.get(field) or " - "}'
                  + str(_("' to '")) + f'{form.cleaned_data.get(field) or " - "}' + "'"
                  for field in form.changed_data]))
            )
        if formsets:
            with translation_override(None):
                for formset in formsets:
                    for added_object in formset.new_objects:
                        change_message.append(
                            str(_('Added' + ': ' + force_text(added_object._meta.verbose_name)))
                            + f' {force_text(added_object)} '
                        )

                    for index, (changed_object, changed_fields) in enumerate(formset.changed_objects):
                        change_message.append(
                            str(_('Changed') + ' ' + force_text(changed_object._meta.verbose_name)
                                + f' {force_text(changed_object)}, fields: ' + ', '.join(
                                [f'{field.replace("_", " ")}: ' + f'{formset[index].cleaned_data.get(field) or " - "}'
                                 + "'"
                                 for field in changed_fields]))
                        )
                    for deleted_object in formset.deleted_objects:
                        change_message.append(
                            change_message.append(
                                str(_('Deleted' + ': ' + force_text(deleted_object._meta.verbose_name)))
                            )
                        )
        return change_message
