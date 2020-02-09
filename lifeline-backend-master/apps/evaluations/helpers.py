from django.utils import translation

from lifeline import settings


def save_evaluation_as_static(evaluations):
    """Function accepts list of evaluations and resaves survey results to static text field.
    :param evaluations: model Evaluation objects
    """
    for evaluation in evaluations:
        if evaluation.survey_type:
            for language in settings.MODELTRANSLATION_LANGUAGES:
                with translation.override(language):
                    evaluation.static_results = str(evaluation.survey_results_display)
            evaluation.name = evaluation.survey_type.name
            evaluation.survey_type = None
            evaluation.is_editable = False
            evaluation.save(update_fields=[
                "static_results",
                "static_results_en",
                "static_results_fr",
                "static_results_nl",
                "name",
                "survey_type",
                "is_editable"
            ])
