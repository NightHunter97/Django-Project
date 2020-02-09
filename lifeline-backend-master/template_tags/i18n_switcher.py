from django import template

register = template.Library()


def switch_lang_code(path, language):
    parts = path.split('/')
    parts[1] = f'{language}/{parts[1]}' if parts[1] == 'admin' else language
    return '/'.join(parts)


@register.filter
def switch_i18n(request, language):
    """takes in a request object and gets the path from it"""
    return switch_lang_code(request.get_full_path(), language)
