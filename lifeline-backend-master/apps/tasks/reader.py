from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.utils.translation import ugettext_lazy as _

from apps.tasks.forms import TaskForm
from apps.tasks.services import get_category_by_slug
from apps.utils.reader import XslxBaseReader


class XslxTaskReader(XslxBaseReader):
    content_error = _('Wrong format')
    no_data_error = _('No data was parsed from file')
    required_field_error = _('English task name is required field')

    header_fields_choices = (
        ('task name en', 'name_en'),
        ('task name fr', 'name_fr'),
        ('task name nl', 'name_nl'),
    )

    def __init__(self, file, user, slug):
        super().__init__(file)
        self.user = user
        self.slug = slug

    @transaction.atomic
    def proceed(self):
        category = get_category_by_slug(self.slug)
        results = []
        if not self._errors:
            try:
                table = self._wb[self._wb.sheetnames[0]]
                data = list(table)
                if self._not_valid_header(data[0]):
                    self._errors.append(_('File has wrong content'))
                    return
                for row in data[1:]:
                    data = {}
                    for index, item in enumerate(list(row)):
                        if not index and not item.value:
                            self._errors.append(self.required_field_error)
                        if item.value:
                            data[self.header_fields_choices[index][1]] = item.value
                            data['category'] = category.pk
                    results.append(data)
                if not results:
                    self._errors.append(self.no_data_error)
                if not self._errors:
                    for result in results:
                        form = TaskForm(result)
                        if form.is_valid():
                            form.save()
                        else:
                            self._errors.append(form.errors.items())
            except IndexError:
                self._errors.append(self.content_error)
            except (ValidationError, IntegrityError) as error:
                self._errors.append(str(error))
