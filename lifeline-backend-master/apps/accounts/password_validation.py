import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class PasswordValidator:
    pattern = '^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[^\w\s]).{8,30}$'

    def validate(self, password, user=None):
        if len(password) < 8 or len(password) > 30:
            raise ValidationError(
                _(f'This password must have 8 - 30 symbols length'),
                code='password_length',
            )

        if not re.match(self.pattern, password):
            raise ValidationError(
                _(f'Must contain 1 lowercase, 1 uppercase letter, 1 symbol and a number.'),
                code='password_too_common',
            )

    def get_help_text(self):
        return _(f'Your password must contain characters 1 lowercase, 1 uppercase, 1 symbol and 8-30 length.')

