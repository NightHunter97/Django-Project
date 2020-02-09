from django.contrib.postgres.fields import JSONField
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from apps.evaluations import choices


class Evaluation(TimeStampedModel):
    """Evaluation Model.
    Model represents results of an evaluation, and stores name of evaluation, patients file,
    results in dynamic or static form, creator and editor of this eval and type of Survey that was used.
    """
    name = models.CharField(verbose_name=_('Evaluation Name'), max_length=255, null=True, blank=True)
    file = models.ForeignKey('patients.File', verbose_name=_('Patient File'), on_delete=models.CASCADE, null=True)
    survey_results = JSONField(verbose_name=_('Surveys results'), null=True)
    static_results = models.TextField(verbose_name=_('Survey static results'), null=True, blank=True)
    user = models.ForeignKey(
        'accounts.User', verbose_name=_('Creator'), related_name='evaluations', on_delete=models.CASCADE, null=True
    )
    edited_by = models.ForeignKey('accounts.User', verbose_name=_('Editor'), on_delete=models.CASCADE, null=True)

    survey_type = models.ForeignKey(
        'evaluations.Survey', verbose_name=_('Type'), related_name='surveys', on_delete=models.SET_NULL,
        null=True, blank=True
    )

    is_editable = models.BooleanField(default=True)

    @property
    def survey_results_display(self):
        """
        :return: if evaluation has survey_type - current survey results in text are fetched from related Survey, else
        returns static results converted to same type as survey results.
        """
        if self.survey_type:
            from apps.evaluations.services import get_survey_by_survey_type, get_survey_question_by_pk,\
                get_question_answer
            survey = get_survey_by_survey_type(self.survey_type.pk)

            return [
                {
                    'question': get_survey_question_by_pk(survey.questions, key),
                    'value': get_question_answer(survey.questions, key, value)
                }
                for key, value in self.survey_results.items()
            ]

        return eval(self.static_results)

    class Meta:
        verbose_name = _('Evaluation')
        verbose_name_plural = _('Evaluations')
        db_table = 'evaluations'
        ordering = ('created',)

    def __str__(self):
        return f'{str(self.file)} ({str(self.file.patient)})'


class Survey(models.Model):
    """
    Survey model represents an individual evaluation form, stores name of survey, is_active to determine if a survey is
    enabled and m2m field groups for object-based permissions.
    Name of the survey has translations.
    """
    name = models.CharField(verbose_name=_('Survey Name'), max_length=255, unique=True)
    is_active = models.BooleanField(verbose_name=_('Enabled'), default=True)
    groups = models.ManyToManyField(
        'auth.Group', verbose_name=_('Groups'), related_name="surveys", blank=True
    )

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')
        db_table = 'surveys'
        ordering = ('id', 'name',)

    def __str__(self):
        return self.name


class Question(models.Model):
    """
    Question model stores survey question and connected to survey via foreign key, stores required flag
    to indicate if question must be answered, category as optional string, question - question itself, and type of
    question (text, choice or date)
    Question has translations.
    """
    survey = models.ForeignKey('evaluations.Survey', on_delete=models.CASCADE, related_name='questions')
    required = models.BooleanField(verbose_name=_('Required'), default=False)
    category = models.CharField(verbose_name=_('Category'), null=True, blank=True, max_length=255)
    question = models.TextField(verbose_name=_('Question'))
    type = models.CharField(verbose_name=_('Question Type'), choices=choices.QUESTION_TYPE,
                            max_length=255, default='text')

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        db_table = 'questions'
        ordering = ('id', 'survey',)

    def __str__(self):
        return self.question


class Answer(models.Model):
    """
    Answer model stores answers to questions with type choice_field and connected to question via foreign key,
    stores text jf an answer.
    Answer has translations.
    """
    question = models.ForeignKey('evaluations.Question', on_delete=models.CASCADE, related_name='answers')
    answer = models.TextField(verbose_name=_('Answer'))

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        db_table = 'answers'
        ordering = ('id', 'answer',)

    def __str__(self):
        return self.answer
