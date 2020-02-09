from modeltranslation.translator import translator, TranslationOptions

from apps.reports.models import Report


class ReportTranslationOptions(TranslationOptions):
    fields = ('report',)


translator.register(Report, ReportTranslationOptions)
