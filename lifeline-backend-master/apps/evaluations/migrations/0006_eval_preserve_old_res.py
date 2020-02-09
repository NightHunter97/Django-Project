# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from django.db import migrations

from lifeline import settings

FROGS_FIELDS = [
    'care_appearance', 'personal_activities', 'housekeeping', 'stress_unforeseen_circumstances', 'travel_communication',
    'diet', 'social_network', 'biological_rythms', 'illness_treatment', 'administrative_financial_management',
    'self_esteem_independence', 'social_activities', 'studying_work', 'family', 'sexual_life',
    'personal_health', 'antisocial_violent_behaviour', 'empathy', 'secondary_effects_of_treatment',
]

FROGS_FIELDS_CHOICES = (
    ('care_appearance', _('Care appearance')),
    ('personal_activities', _('Personal Activities')),
    ('housekeeping', _('Housekeeping')),
    ('stress_unforeseen_circumstances', _('Stress unforeseen circumstances')),
    ('travel_communication', _('Travel communication')),
    ('diet', _('Diet')),
    ('social_network', _('Social network')),
    ('biological_rythms', _('Biological rythms')),
    ('illness_treatment', _('Illness treatment')),
    ('administrative_financial_management', _('Administrative financial management')),
    ('self_esteem_independence', _('Self esteem independence')),
    ('social_activities', _('Social activities')),
    ('studying_work', _('Studying work')),
    ('family', _('Family')),
    ('sexual_life', _('Sexual life')),
    ('personal_health', _('Personal health')),
    ('antisocial_violent_behaviour', _('Antisocial violent behaviour')),
    ('empathy', _('Empathy')),
    ('secondary_effects_of_treatment', _('Secondary effects of treatment'))
)

FROGS_VALUES = {
    ('dont', _('Do not do')),
    ('part', _('Do partially')),
    ('significant', _('Do a significant part')),
    ('almost', _('Do almost all the activity')),
    ('perfect', _('Do perfectly'))
}

CANFOR_FIELDS_CHOICES = (
    ('accomodation', _('Accomodation')),
    ('alimentation', _('Alimentation')),
    ('living_environment', _('Living environment')),
    ('self_care', _('Self-care')),
    ('daytime_activities', _('Daytime activities')),
    ('physical_health', _('Physical health')),
    ('psychotic_symptoms', _('Psychotic symptoms')),
    ('condition_and_treatment', _('Condition_and treatment')),
    ('psychological_distress', _('Psychological distress')),
    ('safety_to_self', _('Safety to self')),
    ('safety_to_others', _('Safety to others')),
    ('alcohol', _('Alcohol')),
    ('drugs', _('Drugs')),
    ('company', _('Company')),
    ('intimate_relationships', _('Intimate relationships')),
    ('sexual_expression', _('Sexual expression')),
    ('childcare', _('Childcare')),
    ('basic_education', _('Basic education')),
    ('telephone', _('Telephone')),
    ('transport', _('Transport')),
    ('money', _('Money')),
    ('benefits', _('Benefits')),
    ('treatment', _('Treatment')),
    ('sexual_offences', _('Sexual offences')),
    ('arson', _('Arson'))
)

CANFOR_VALUES = (
    ('no_need', _('No need for this area')),
    ('met_need', _('Met need for this area')),
    ('unmet', _('Unmet need for this area')),
    ('not_accept', _('Not applicable')),
    ('unknown', _('Unknown'))
)

KATZ_FIELDS_CHOICES = (
    ('bathing', _('Bathing')),
    ('dressing', _('Dressing')),
    ('transferring', _('Transferring')),
    ('toiletting', _('Toiletting')),
    ('continence', _('Continence')),
    ('feeding', _('Feeding')),
    ('orientation_in_time', _('Orientation in time')),
    ('orientation_in_place', _('Orientation in place')),
)

KATZ_MAPPING = {
    'bathing': (
        ('self', _('Bathes self completely without any help')),
        ('partial', _('Needs partial help with bathing above or below waist')),
        ('deep_partial', _('Needs partial help with bathing above and also below waist')),
        ('total', _('Needs total bathing both above and below waist')),
    ),
    'dressing': (
        ('self', _('Dresses and undresses self completely without any help')),
        ('partial',
         _('Needs partial help with dressing self above or below waist (may have help tying shoes)')),
        ('deep_partial', _('Needs partial help with dressing self above and also below waist')),
        ('total', _('Needs to be completely dressed both above and below waist')),
    ),
    'transferring': (
        ('self', _('Moves alone in and out of bed without any help or mechanical transferring aides')),
        ('partial',
         _('Moves alone in and out of bed with mechanical transferring aides (crutches, wheelchair...)')),
        ('deep_partial', _('Needs help with moving from bed to chair or from chair to bed, and/or for other transferring')),
        ('total', _('Is bedridden or in a wheelchair and is highly dependant on someone\'s help'))
    ),
    'toiletting': (
        ('self', _('Goes to toilet, gets on and off, arranges clothes and cleans genital area without help')),
        ('partial', _('Needs help with one these : transferring to the toilet, arrange clothes or clean genital area')),
        ('deep_partial',
         _('Needs help with two of these : transferring to the toilet, arrange clothes or clean genital area')),
        ('total', _('Needs help with all these : transferring to the toilet, arrange clothes or clean genital area'))
    ),
    'continence': (
        ('self', _('Exercise complete self control over urination and defecation')),
        ('partial', _('Is accidentally incontinent of bladder or bowel (urinary catheter or colostomy included)')),
        ('deep_partial', _('Is incontinent of bladder (including urination exercises) or bowel')),
        ('total', _('Is totally incontinent of bladder and bowel'))
    ),
    'feeding': (
        ('self', _('Is able to eat and drink without any help')),
        ('partial', _('Needs partial help with preparation for eating or drinking')),
        ('deep_partial', _('Needs partial help while eating or drinking')),
        ('total', _('Needs total help with eating or drinking'))
    ),
    'orientation_in_time': (
        ('self', _('No problem')),
        ('partial', _('From time to time, rarely problems')),
        ('deep_partial', _('Problems almost every day')),
        ('total', _('Totally disoriented or impossible to evaluate'))
    ),
    'orientation_in_place': (
        ('self', _('No problem')),
        ('partial', _('From time to time, rarely problems')),
        ('deep_partial', _('Problems almost every day')),
        ('total', _('Totally disoriented or impossible to evaluate'))
    )
}


def get_proper_vals(choices, values, evaluation, if_katz):
    if evaluation:
        if not if_katz:
            return [
                {
                    'question': dict(choices).get(key),
                    'value': dict(values).get(value)
                } for key, value in evaluation.items() if key and value
            ]
        return [
            {
                'question': dict(choices).get(key),
                'value': dict(values.get(key)).get(value)
            } for key, value in evaluation.items() if key and value
        ]


def set_static_to_old(evaluation, choices, values, old_evaluation, if_katz):
        for language in settings.MODELTRANSLATION_LANGUAGES:
            with translation.override(language):
                old_eval = get_proper_vals(choices, values, old_evaluation, if_katz)

                if language is 'en':
                    evaluation.static_results_en = str(old_eval)

                if language is 'fr':
                    evaluation.static_results_fr = str(old_eval)

                if language is 'nl':
                    evaluation.static_results_nl = str(old_eval)

        return evaluation


def re_safe_old_evals(apps, schema_editor):
    evaluations = apps.get_model('evaluations', 'Evaluation')
    for evaluation in evaluations.objects.all():

        canfor_params = (CANFOR_FIELDS_CHOICES, CANFOR_VALUES, evaluation.canfor, False)
        frogs_params = (FROGS_FIELDS_CHOICES, FROGS_VALUES, evaluation.frogs, False)
        katz_params = (KATZ_FIELDS_CHOICES, KATZ_MAPPING, evaluation.katz, True)

        old_evaluations = [(evaluation.canfor, "Canfor", canfor_params), (evaluation.frogs, "Frogs", frogs_params),
                           (evaluation.katz, "Katz", katz_params)]

        for old_evaluation in old_evaluations:
            if old_evaluation[0] and len(old_evaluation[0]) > 0:
                new_evaluation = evaluations.objects.create(name=f'{old_evaluation[1]} old', file=evaluation.file,
                                                            user=evaluation.user, survey_type=None, result=5)

                new_evaluation = set_static_to_old(new_evaluation, old_evaluation[2][0],
                                                   old_evaluation[2][1], old_evaluation[2][2], old_evaluation[2][3])

                new_evaluation.save(update_fields=["static_results_en", "static_results_fr",
                                                   "static_results_nl", "name"])

        evaluation.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0005_auto_20190521_1413'),
    ]

    operations = [
        migrations.RunPython(re_safe_old_evals, reverse_code=migrations.RunPython.noop),
    ]
