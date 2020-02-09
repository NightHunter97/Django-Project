from modeltranslation.translator import translator, TranslationOptions

from apps.medications.models import Drug


class DrugTranslationOptions(TranslationOptions):
    fields = ('unit',)


translator.register(Drug, DrugTranslationOptions)
