from modeltranslation.translator import translator, TranslationOptions

from apps._messages.models import AboutPatient


class AboutPatientTranslationOptions(TranslationOptions):
    fields = ('subject',)


translator.register(AboutPatient, AboutPatientTranslationOptions)
