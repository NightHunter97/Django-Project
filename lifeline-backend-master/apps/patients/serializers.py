import datetime

from django.db.models import Q
from rest_framework import serializers
from rest_framework.fields import empty

from apps.accounts.serializers import UserSerializer
from apps.brusafe.services import patient_user_relation
from apps.patients import choices
from apps.patients.models import Patient, File, ArchiveComment, EmergencyContact
from apps.patients.services import does_email_exist, create_file_for_patient, get_active_patient_file, already_has_file, \
    update_file_unit, get_patient, get_file_by_file_id
from django.utils.translation import ugettext_lazy as _

from apps.units.models import Unit
from apps.units.services import get_unit_by_name, get_unit
from apps.utils.mixins import FileValidationMixin


class PatientBaseSerializer(serializers.ModelSerializer):

    patient_id = serializers.CharField(required=False, allow_null=True)
    full_name = serializers.CharField(required=True, max_length=255)
    birth_date = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    post_code = serializers.CharField(required=True)
    unit = serializers.CharField(required=False)
    insurance_policy = serializers.CharField(required=False, allow_blank=True)
    file = serializers.CharField(required=False)
    email = serializers.CharField(required=False, allow_null=True)
    has_relation = serializers.SerializerMethodField()
    national_register = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Patient
        fields = (
           'full_name', 'patient_id', 'card_number', 'card_type', 'document_type', 'language', 'birth_date', 'unit',
           'gender', 'marital_status', 'partner_name', 'nationality', 'country', 'address', 'post_code',
           'national_register', 'foreign_register', 'phone_number', 'email', 'is_vip', 'religion',
           'general_practitioner', 'death_date', 'note', 'insurance_policy', 'policy_holder', 'validity_end',
           'beneficiary_id', 'beneficiary_occupation', 'heading_code', 'is_employed', 'dependants',
           'is_third_party_auth', 'disability_recognition', 'regional_recognition', 'disability_assessment_points',
           'income_origin', 'income_amount', 'expenses', 'debts', 'attorney', 'management', 'admission', 'occupation',
           'career', 'education', 'edu_pathway', 'file', 'has_relation'
        )

    def create(self, validated_data):
        patient_id = validated_data.pop('patient_id', None)
        instance = get_patient(patient_id)
        if instance:
            return self.update(instance, validated_data)
        unit = validated_data.pop('unit', None)
        if isinstance(unit, str):
            try:
                unit = int(unit)
                unit = get_unit(unit)
            except ValueError:
                unit = get_unit_by_name(unit) or Unit.objects.create(name=unit)
            unit = unit.pk
        instance = super().create(validated_data)
        create_file_for_patient(instance, unit)
        return instance

    def update(self, instance, validated_data):
        unit = validated_data.pop('unit', None)
        if isinstance(unit, str):
            try:
                unit = int(unit)
                unit = get_unit(unit)
            except ValueError:
                unit = get_unit_by_name(unit) or Unit.objects.create(name=unit)
            unit = unit.pk
        instance = super().update(instance, validated_data)

        if not already_has_file(instance) and not self.partial:
            create_file_for_patient(instance, unit)

        try:
            file_id = self.context['request'].data.get('file_id')
            file = File.objects.filter(file_id=file_id).first()
        except KeyError:
            file = get_active_patient_file(instance)

        if file and unit and file.unit and file.unit.pk != unit:
            update_file_unit(file, unit)

        return instance

    def validate_email(self, email):
        pk = self.instance.id if self.instance else None
        if does_email_exist(email, self.initial_data.get('patient_id'), pk):
            raise serializers.ValidationError(_('Email already exists'))
        return email

    def validate_national_register(self, value):
        patient = self._kwargs.get('context')['request'].data.get('selectedPatient')
        pk = self.instance.pk if self.instance else None
        patient_id = patient.get('patient_id') if patient else None
        if Patient.objects.filter(national_register=value).exclude(Q(pk=pk) | Q(patient_id=patient_id)).exists():
            raise serializers.ValidationError(_('This field must be unique.'))

        if not self.initial_data.get('national_register'):
            return None

        return value

    def validate_insurance_policy(self, policy):
        if self.initial_data.get('insurance_policy') in dict(choices.HEALTH_INSURANCE):
            return self.initial_data['insurance_policy']

    def get_has_relation(self, obj):
        context = self._kwargs.get('context')
        if context:
            return patient_user_relation(obj.pk, context['request'].user.uuid)


class LightPatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = ('full_name', 'patient_id', 'gender')


class FileListSerializer(serializers.ModelSerializer):

    patient = LightPatientSerializer()
    birth_date = serializers.SerializerMethodField()
    admission = serializers.SerializerMethodField()
    closing = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    unit = serializers.CharField()

    class Meta:
        model = File
        fields = (
            'patient',
            'file_id',
            'unit',
            'open_tasks',
            'due_tasks',
            'bed',
            'birth_date',
            'admission',
            'closing',
            'status',
            'due_tasks',
            'open_tasks'
        )

    @staticmethod
    def get_status(obj):
        if obj.is_released:
            return _('Released')
        if obj.is_temporary:
            return _('Temporary released')
        return _('Present')

    @staticmethod
    def get_birth_date(obj):
        birth_date = obj.patient.birth_date
        if birth_date:
            return birth_date

    @staticmethod
    def get_admission(obj):
        return obj.created.date()

    @staticmethod
    def get_closing(obj):
        return obj.closed_since


class PatientDetailSerializer(PatientBaseSerializer):

    unit = serializers.SerializerMethodField()
    file_id = serializers.CharField(required=True)
    card_type_display = serializers.CharField(source='get_card_type_display')
    document_type_display = serializers.CharField(source='get_document_type_display')
    language_display = serializers.CharField(source='get_language_display')
    gender_display = serializers.CharField(source='get_gender_display')
    marital_status_display = serializers.CharField(source='get_marital_status_display')
    nationality_display = serializers.CharField(source='get_nationality_display')
    country_display = serializers.CharField(source='get_country_display')
    religion_display = serializers.CharField(source='get_religion_display')
    insurance_policy_display = serializers.CharField(source='get_insurance_policy_display')
    beneficiary_occupation_display = serializers.CharField(source='get_beneficiary_occupation_display')
    heading_code_display = serializers.CharField(source='get_heading_code_display')
    dependants_display = serializers.CharField(source='get_dependants_display')
    income_origin_display = serializers.CharField(source='get_income_origin_display')
    admission_display = serializers.CharField(source='get_admission_display')
    education_display = serializers.CharField(source='get_education_display')
    edu_pathway_display = serializers.CharField(source='get_edu_pathway_display')
    is_released = serializers.BooleanField(read_only=True)
    unit_display = serializers.SerializerMethodField()
    bed = serializers.SerializerMethodField()
    admission_date = serializers.SerializerMethodField()
    stay = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
           'full_name', 'patient_id', 'card_number', 'card_type', 'document_type', 'language', 'birth_date', 'unit',
           'unit_display', 'gender', 'marital_status', 'partner_name', 'nationality', 'country', 'address', 'post_code',
           'national_register', 'foreign_register', 'phone_number', 'email', 'is_vip', 'religion',
           'general_practitioner', 'death_date', 'note', 'insurance_policy', 'policy_holder', 'validity_end',
           'beneficiary_id', 'beneficiary_occupation', 'heading_code', 'is_employed', 'dependants',
           'is_third_party_auth', 'disability_recognition', 'regional_recognition', 'disability_assessment_points',
           'income_origin', 'income_amount', 'expenses', 'debts', 'attorney', 'management', 'admission', 'occupation',
           'career', 'education', 'edu_pathway', 'file_id', 'bed', 'admission_date', 'stay', 'age', 'card_type_display',
           'document_type_display', 'language_display', 'gender_display', 'marital_status_display',
           'nationality_display', 'country_display', 'religion_display', 'insurance_policy_display',
           'beneficiary_occupation_display', 'heading_code_display', 'dependants_display', 'income_origin_display',
           'admission_display', 'education_display', 'edu_pathway_display', 'is_released', 'has_relation',
           'is_gdpr_agreed'
        )

    def __init__(self, instance=None, data=empty, **kwargs):
        self.file = File.objects.filter(file_id=instance.file_id).first()
        super().__init__(instance=instance, data=data, **kwargs)

    def get_admission_date(self, obj):
        if self.file:
            return self.file.created.date()

    def get_stay(self, obj):
        return (datetime.date.today() - obj.created.date()).days

    def get_birth_date(self, obj):
        if obj.birth_date:
            return obj.birth_date

    def get_age(self, obj):
        if obj.birth_date:
            years_diff = datetime.datetime.now().year - obj.birth_date.year
            if self._was_the_birthday(obj.birth_date):
                return years_diff
            return years_diff - 1

    def _was_the_birthday(self, birthday):
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        return birthday.month < month or (birthday.month == month and birthday.day <= day)

    def get_bed(self, obj):
        if self.file:
            return self.file.bed

    def get_unit(self, obj):
        if obj.unit and isinstance(obj.unit, str):
            return obj.unit
        if self.file and self.file.unit:
            return self.file.unit.id

    def get_unit_display(self, obj):
        if obj.unit and isinstance(obj.unit, str):
            unit = Unit.objects.get(id=obj.unit)
            return unit.name
        if self.file and self.file.unit:
            return self.file.unit.name


class PatientSerializer(PatientBaseSerializer):
    unit = serializers.SerializerMethodField()
    info = (
        'full_name', 'patient_id', 'unit', 'card_number', 'card_type', 'document_type', 'language', 'birth_date',
        'gender',
        'marital_status', 'partner_name', 'nationality', 'country', 'address', 'post_code', 'national_register',
        'foreign_register', 'phone_number', 'email', 'is_vip', 'religion', 'general_practitioner', 'death_date', 'note'
    )
    insurance = (
        'insurance_policy', 'policy_holder', 'validity_end', 'beneficiary_id', 'beneficiary_occupation', 'heading_code',
        'is_employed', 'dependants', 'is_third_party_auth'
    )
    social = (
        'disability_recognition', 'regional_recognition', 'disability_assessment_points', 'income_origin',
        'income_amount', 'expenses', 'debts', 'attorney', 'management', 'admission', 'occupation', 'career',
        'education', 'edu_pathway'
    )
    all = '__all__'

    class Meta:
        model = Patient
        fields = ('full_name', 'patient_id')

    def __init__(self, instance=None, data=empty, **kwargs):
        step = kwargs['context']['request'].query_params.get('step', '')
        self.Meta.fields = getattr(self, step, ('full_name', 'patient_id'))
        super().__init__(instance, data, **kwargs)

    def get_unit(self, obj):
        file = get_active_patient_file(obj)
        if file and file.unit:
            return file.unit.id


class ArchiveCommentSerializer(FileValidationMixin, serializers.ModelSerializer):
    file_id = serializers.CharField(write_only=True)
    created_by = serializers.CharField(read_only=True)
    file = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = ArchiveComment
        fields = ('comment', 'created', 'user', 'file_id', 'file', 'created_by')

    def create(self, validated_data):
        validated_data['user'] = self._kwargs['context']['request'].user
        return super().create(validated_data)

    @staticmethod
    def get_file(obj):
        return obj.file.file_id


class FileStatusSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = File
        fields = ('closed_since', 'temporary_released_start', 'temporary_released_end', 'description')

    def update(self, instance, validated_data):
        validated_data.pop('description', None)
        if not validated_data.get('temporary_released_end') and not validated_data.get('temporary_released_start'):
            validated_data['closed_since'] = datetime.datetime.now().date()
        return super().update(instance, validated_data)

    def validate_temporary_released_start(self, value):
        if not self.initial_data.get('temporary_released_end'):
            raise serializers.ValidationError(_('Released to is required'))
        return value

    def validate_temporary_released_end(self, value):
        if not self.initial_data.get('temporary_released_start'):
            raise serializers.ValidationError(_('Released from is required'))
        return value


class EmergencyContactSerializer(FileValidationMixin, serializers.ModelSerializer):
    file = serializers.CharField(required=True, write_only=True)
    patient = serializers.CharField(required=False, read_only=True)
    user = UserSerializer(read_only=True, source='creator')

    class Meta:
        model = EmergencyContact
        fields = (
            'file', 'patient', 'relation', 'name', 'phone', 'email', 'id', 'get_relation_display', 'trusted', 'user'
        )

    def create(self, validated_data):
        file = get_file_by_file_id(validated_data.pop('file'))
        if file:
            validated_data['patient'] = get_file_by_file_id(file).patient
            validated_data['creator'] = self._kwargs['context']['request'].user
        return super().create(validated_data)
