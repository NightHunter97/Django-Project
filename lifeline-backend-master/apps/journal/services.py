from apps.journal.models import Journal


def get_journal_notes():
    return Journal.objects.all()


def create_journal_message(name_en, name_fr, name_nl, content, file, user, category, action, **kwargs):
    return Journal.objects.create(
        name_en=name_en,
        name_fr=name_fr,
        name_nl=name_nl,
        content=content, file=file, user=user, category=category, action=action,
        type=kwargs.get('type', 'comment')
    )
