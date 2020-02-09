from modeltranslation.translator import translator, TranslationOptions

from apps.diagnostics.models import Diagnose, HealthScreening


class DiagnoseTranslationOptions(TranslationOptions):
    fields = ('term',)


class HealthScreeningOptions(TranslationOptions):
    fields = ('term',)


translator.register(Diagnose, DiagnoseTranslationOptions)
translator.register(HealthScreening, HealthScreeningOptions)
