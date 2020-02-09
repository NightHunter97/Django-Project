from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.forms import model_to_dict

from apps.evaluations.models import Survey, Evaluation, Question, Answer
from apps.evaluations.helpers import save_evaluation_as_static


def is_proceed(instance):
    if isinstance(instance, Survey):
        try:
            old_instance = model_to_dict(Survey.objects.get(id=instance.id))
        except Survey.DoesNotExist:
            return False
        instance = model_to_dict(instance)
        changed_fields = [key for key, value in instance.items() if instance.get(key) != old_instance.get(key)]
        return not(len(changed_fields) is 0)
    return True


@receiver(pre_save, sender=Evaluation)
@receiver([pre_save, pre_delete], sender=Answer)
@receiver([pre_save, pre_delete], sender=Question)
@receiver([pre_save, pre_delete], sender=Survey)
def evaluation_to_static(sender, instance, **kwargs):
    """Reciver for any updates of Evaluations, Surveys, questions and Answers.
    Calls saving evaluation results as static
    """
    try:
        id = instance.question.survey.id
    except AttributeError:
        try:
            id = instance.survey.id
        except AttributeError:
            try:
                id = instance.survey_type.id
            except AttributeError:
                id = instance.id

    evaluations = Evaluation.objects.filter(survey_type__id=id)
    if isinstance(instance, Evaluation):
        evaluations = evaluations.filter(file__file_id=instance.file.file_id).exclude(id=instance.id)

    if is_proceed(instance):
        save_evaluation_as_static(evaluations)
