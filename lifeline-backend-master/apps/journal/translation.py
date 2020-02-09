from modeltranslation.translator import translator, TranslationOptions
from apps.journal.models import Journal


class JournalTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Journal, JournalTranslationOptions)
