from django import forms

from apps.patients import choices
from apps.patients.models import Patient


class PatientForm(forms.ModelForm):

    gender = forms.ChoiceField(choices=(('', '--------'), choices.SEX[0], choices.SEX[2]), required=False)

    class Meta:
        model = Patient
        fields = (
            'full_name',
            'birth_date',
            'language',
            'gender',
            'marital_status',
            'card_number',
            'document_type',
            'card_type',
            'national_register',
            'partner_name',
            'address',
            'country',
            'post_code',
            'nationality',
            'foreign_register',
            'phone_number',
            'email',
            'is_vip',
            'religion',
            'death_date',
            'general_practitioner',
            'insurance_policy',
            'heading_code',
            'beneficiary_id',
            'beneficiary_occupation',
            'is_employed',
            'dependants',
            'policy_holder',
            'validity_end',
            'is_third_party_auth',
            'disability_recognition',
            'disability_assessment_points',
            'regional_recognition',
            'income_origin',
            'income_amount',
            'expenses',
            'debts',
            'attorney',
            'management',
            'admission',
            'occupation',
            'career',
            'education',
            'edu_pathway'
        )
