import datetime

from rest_framework import serializers

from apps.patients import choices
from apps.patients.models import Patient, File
from apps.patients.services import create_file_for_patient
from apps.units.models import Unit
from apps.wish.hl7_tools import time_convert
from django.utils.translation import ugettext_lazy as _


class PatientFromHL7Serializer(serializers.ModelSerializer):
    """Serializer for patient info from .hl7 file."""
    full_name = serializers.CharField(required=True, max_length=255)
    birth_date = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    post_code = serializers.CharField(required=False)
    insurance_policy = serializers.CharField(required=False, allow_blank=True)
    national_register = serializers.CharField(required=True)
    is_vip = serializers.CharField(required=False, allow_null=True)
    validity_end = serializers.CharField(required=False, allow_null=True)
    is_employed = serializers.CharField(required=False, allow_null=True)
    marital_status = serializers.CharField(required=False, allow_null=True)
    country = serializers.CharField(required=False)
    created = serializers.CharField(required=False)

    class Meta:
        model = Patient
        fields = (
           'full_name', 'card_number', 'card_type', 'document_type', 'language', 'birth_date',
           'gender', 'marital_status', 'partner_name', 'nationality', 'country', 'address', 'post_code',
           'national_register', 'foreign_register', 'phone_number', 'is_vip', 'religion',
           'death_date', 'insurance_policy', 'policy_holder', 'validity_end',
           'beneficiary_id', 'is_employed', 'expenses', 'created'
        )

    def create(self, validated_data):
        created = validated_data.get('created') or datetime.datetime.now()
        instance = super().create(validated_data)
        file = create_file_for_patient(instance, None)
        file.created = created
        file.save()

        return instance

    def validate_insurance_policy(self, policy):
        if self.initial_data.get('insurance_policy') in dict(choices.HEALTH_INSURANCE):
            return self.initial_data['insurance_policy']

    def validate_created(self, created):
        """Validates creation date."""
        created = time_convert(created)
        if not created:
            raise serializers.ValidationError(_('Wrong date format for created'))
        return created

    def validate_national_register(self, national_register):
        """Validates that patient has a national_register for identification."""
        if not national_register:
            raise serializers.ValidationError(_('Patient from hl7 must have national_register'))
        return national_register

    def validate_is_vip(self, is_vip):
        """Temp version of is_vip, until it is known what can be in this field."""
        if is_vip:
            return True
        return False

    def validate_is_employed(self, is_employed):
        """Temp version of is_employed, until it is known what can be in this field."""
        if is_employed in ("T", "3", "9", None):
            return False
        return True

    def validate_birth_date(self, birth_date):
        """Validator for birth_date ensures wright format of birth_date"""
        date = time_convert(birth_date)
        if not date:
            raise serializers.ValidationError(_('Wrong date format for birth_date'))
        return date

    def validate_validity_end(self, validity_end):
        """Validator for validity_end ensures wright format of validity_end"""
        date = time_convert(validity_end)
        if not date:
            raise serializers.ValidationError(_('Wrong date format for validity_end'))
        return date

    def validate_marital_status(self, marital_status):
        if marital_status is "S":
            return "SI"

        if marital_status in ("A", "E"):
            return "SE"

        if marital_status in ("G", "P", "R"):
            return "H"

        if marital_status in ("N", "I", "B", "O", "T"):
            return "U"

        return marital_status


class FileHL7Serializer(serializers.ModelSerializer):
    closed_since = serializers.DateField(required=False, allow_null=True)
    temporary_released_start = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    temporary_released_end = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bed = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    unit = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = File
        fields = ('closed_since', 'temporary_released_start', 'temporary_released_end',
                  'bed', 'status', 'temporary_location', 'unit')

    def validate_unit(self, unit):
        unit = Unit.objects.get_or_create(name=unit)[0]
        return unit

    def validate_closed_since(self, closed_since):
        """Ensures that closed_since is actually in the past."""
        if closed_since:
            if closed_since > datetime.date.today():
                raise serializers.ValidationError(_('Closed time cant be in future'))
        return closed_since

    def validate_temporary_released_start(self, temporary_released_start):
        """Date format adapter for DB, validates that there is an end date"""
        value = time_convert(temporary_released_start)
        if not value:
            raise serializers.ValidationError(_('Wrong date format for validity_end'))
        return value

    def validate_temporary_released_end(self, temporary_released_end):
        """Date format adapter for DB, validates that there is a start date"""
        value = time_convert(temporary_released_end)
        if not value:
            raise serializers.ValidationError(_('Wrong date format for validity_end'))
        return value