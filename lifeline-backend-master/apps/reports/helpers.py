from apps.diagnostics.services import get_diagnostics_by_file
from apps.evaluations.services import get_all_last_evaluations_for_file
from apps.medications.services import get_all_prescriptions_by_file
from apps.tasks.services import get_all_tasks_by_file
from apps.vitals.services import get_last_vitals_by_file
from apps.wounds.services import get_filtered_wounds


class ReportContextHelper:

    @classmethod
    def get_specification_context(cls, file):
        return {
            'medical': {
                'diagnostics': get_diagnostics_by_file(file),
                'vitals': get_last_vitals_by_file(file),
                'wounds': get_filtered_wounds(False, file),
                'medications': get_all_prescriptions_by_file(file),
                'tasks': get_all_tasks_by_file(file)
            },
            'social': {},
            'drugs': {
                'medications': get_all_prescriptions_by_file(file),
            },
            'evaluation': {'evals': cls._get_survey_results(file)}
        }

    @staticmethod
    def _get_survey_results(file):
        evaluations = get_all_last_evaluations_for_file(file.file_id)
        if evaluations:
            res = {evaluation.survey_type.name: evaluation.survey_results_display
                   for evaluation in evaluations if evaluation.is_editable}
            res.update({f'{evaluation.name} old': evaluation.survey_results_display
                        for evaluation in evaluations if not evaluation.is_editable})
            return res
