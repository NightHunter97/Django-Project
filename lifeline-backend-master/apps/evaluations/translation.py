from modeltranslation.translator import translator, TranslationOptions

from apps.evaluations.models import Survey, Question, Answer, Evaluation


class EvaluationTranslationOptions(TranslationOptions):
    fields = ('static_results',)


class SurveyTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en',)


class QuestionTranslationOptions(TranslationOptions):
    fields = ('question',)
    required_languages = ('en',)


class AnswerTranslationOptions(TranslationOptions):
    fields = ('answer',)
    required_languages = ('en',)


translator.register(Evaluation, EvaluationTranslationOptions)
translator.register(Survey, SurveyTranslationOptions)
translator.register(Question, QuestionTranslationOptions)
translator.register(Answer, AnswerTranslationOptions)
