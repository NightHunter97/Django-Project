import base64
import six

from mimetypes import guess_extension, guess_type
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64FileField(serializers.FileField):
    ext_mapping = {
        '.jpe': '.jpg'
    }

    def to_internal_value(self, payload):
        if isinstance(payload, six.string_types):
            try:
                data_list = payload.split(';name;')
                file_name = data_list[0]
                data = data_list[1]
                file_extension = ''
                if 'data:' in data and ';base64,' in data:
                    header, data = data.split(';base64,')
                    file_extension = guess_extension(guess_type(f'{header};base64,')[0])
                    file_extension = self.ext_mapping.get(file_extension, file_extension)
                try:
                    decoded_file = base64.b64decode(data)
                except TypeError:
                    self.fail('invalid_file')

                complete_file_name = f'{file_name}{file_extension}'
                data = ContentFile(decoded_file, name=complete_file_name)
            except IndexError:
                data = None
            return super().to_internal_value(data)
