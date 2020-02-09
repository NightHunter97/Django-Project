from datetime import datetime

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from apps.patients import choices


class Patient(TimeStampedModel):
    """
    Patient model stores all of the not visit specific information about patient, his insurance and social information.
    """
    patient_id = models.CharField(_('Patient ID'), max_length=10, unique=True)
    full_name = models.CharField(_('Full name'), max_length=255, db_index=True, blank=True, null=True)
    card_number = models.CharField(_('Identity Card Number'), max_length=255, blank=True, null=True)
    card_type = models.CharField(
        _('Identity Card Type'), choices=choices.CARD_TYPES, max_length=7, blank=True, null=True
    )
    document_type = models.CharField(
        _('Identity Document Type'), choices=choices.DOCUMENT_TYPES, max_length=7, blank=True, null=True
    )
    language = models.CharField(_('Language'), choices=choices.LANGUAGES, max_length=7, blank=True, null=True)
    birth_date = models.DateField(_('Birth Date'), auto_now=False, auto_now_add=False, blank=True, null=True)
    gender = models.CharField(_('Gender'), choices=choices.SEX, max_length=7, db_index=True, blank=True, null=True)
    marital_status = models.CharField(
        _('Marital Status'), choices=choices.MARITAL_STATUSES, max_length=7, blank=True, null=True
    )
    partner_name = models.CharField(_('Partner\'s Name'), max_length=128, blank=True, null=True)
    nationality = models.CharField(_('Nationality'), choices=choices.COUNTRIES, max_length=255, blank=True, null=True)
    country = models.CharField(_('Country'), choices=choices.COUNTRIES, max_length=255, blank=True, null=True)
    address = models.CharField(_('Address'), max_length=255, blank=True, null=True)
    post_code = models.CharField(_('Post Code'), max_length=255, blank=True, null=True)
    national_register = models.CharField(_('National Register'), max_length=255, blank=True, null=True, unique=True)
    foreign_register = models.CharField(_('Foreign Register'), max_length=255, blank=True, null=True)
    phone_number = models.CharField(_('Phone Number'), max_length=128, blank=True, null=True)
    email = models.EmailField(_('E-mail Address'), max_length=128, blank=True, null=True, unique=True)
    is_vip = models.BooleanField(_('Confidential(VIP)'), default=False)
    religion = models.CharField(_('Religion'), choices=choices.RELIGIONS, max_length=7, blank=True, null=True)
    general_practitioner = models.CharField(_('General Practitioner'), max_length=128, blank=True, null=True)
    death_date = models.DateField(_('Date of Death'), auto_now=False, auto_now_add=False, blank=True, null=True)
    note = models.TextField(_('Note'), null=True, blank=True)

    insurance_policy = models.CharField(
        _('Health Insurance Policy'), choices=choices.HEALTH_INSURANCE, max_length=10, blank=True, null=True
    )
    policy_holder = models.CharField(_('Policy Holder Name'), max_length=128, blank=True, null=True)
    validity_end = models.DateField(
        _('End of Validity Period'), auto_now=False, auto_now_add=False, blank=True, null=True
    )
    beneficiary_id = models.CharField(_('Beneficiary ID'), max_length=128, blank=True, null=True)
    beneficiary_occupation = models.CharField(
        _('Beneficiary occupation'), choices=choices.OCCUPATIONS, max_length=7, blank=True, null=True
    )
    heading_code = models.CharField(
        _('Heading Code HC1/HC2'), choices=choices.HEADING_HEALTH_INSURANCE, max_length=128, blank=True, null=True
    )
    is_employed = models.BooleanField(_('Employed/Unemployed'), default=False)
    dependants = models.CharField(_('Dependants'), choices=choices.DEPENDANTS, max_length=7, blank=True, null=True)
    is_third_party_auth = models.BooleanField(_('Authorised Third Party'), default=False)

    disability_recognition = models.BooleanField(_('Federal Disability Recognition'), default=False)
    regional_recognition = models.BooleanField(_('Regional Disability Recognition'), default=False)
    disability_assessment_points = models.CharField(
        _('Disability Assessment points'), max_length=255, blank=True, null=True
    )
    income_origin = models.CharField(
        _('Income origin'), choices=choices.INCOME_ORIGIN, max_length=7, blank=True, null=True
    )
    income_amount = models.CharField(_('Income amount'), max_length=255, blank=True, null=True)
    expenses = models.CharField(_('Expenses'), max_length=255, blank=True, null=True
                                )
    debts = models.BooleanField(_('Debts'), default=False)
    attorney = models.BooleanField(_('Financial Power of Attorney'), default=False)
    management = models.CharField(_('Financial Management'), max_length=255, blank=True, null=True)
    admission = models.CharField(
        _('Living Environment ad Admission'), choices=choices.ADMISSION, max_length=7, blank=True, null=True
    )
    occupation = models.CharField(_('Current Occupation'), max_length=255, blank=True, null=True)
    career = models.CharField(_('Professional Career'), max_length=255, blank=True, null=True)
    education = models.CharField(_('Education'), choices=choices.EDUCATION, max_length=7, blank=True, null=True)
    edu_pathway = models.CharField(
        _('Education Pathway'), choices=choices.EDUCATION_PATHWAY, max_length=7, blank=True, null=True
    )
    is_gdpr_agreed = models.BooleanField(_('Consent to proceed patient data'), default=True)

    def __str__(self):
        return self.full_name or self.patient_id

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = self._get_unique_patient_id()
        return super().save(*args, **kwargs)

    def _get_unique_patient_id(self):
        unique = self._get_random_patient_id()
        while unique in self._meta.model.objects.values_list('patient_id', flat=True):
            unique = self._get_random_patient_id()
        return unique

    @staticmethod
    def _get_random_patient_id():
        return get_random_string(length=6, allowed_chars='0123456789')

    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')
        db_table = 'patients'
        ordering = ('-created',)


class File(TimeStampedModel):
    """
    File model contains information about patients visit.
    """
    patient = models.ForeignKey(
        'patients.Patient', verbose_name=_('Patient'), related_name="files", on_delete=models.CASCADE
    )
    file_id = models.CharField(_('File ID'), max_length=10, unique=True)
    unit = models.ForeignKey('units.Unit', verbose_name=_('Unit'), null=True, blank=True, on_delete=models.CASCADE)
    closed_since = models.DateField(_('Closed since'), blank=True, null=True)
    temporary_released_start = models.DateField(_('Released from'), blank=True, null=True)
    temporary_released_end = models.DateField(_('Released until'), blank=True, null=True)
    bed = models.CharField(_("Assigned Patient's Bed"), max_length=256, blank=True, null=True)
    status = models.CharField(_('Status'), choices=choices.PATIENT_STATUSES, max_length=7, blank=True, null=True)
    temporary_location = models.CharField(_("Temporary patients location"), max_length=256, blank=True, null=True)
    due_tasks = models.IntegerField(_('Due tasks'), default=0)
    open_tasks = models.IntegerField(_('Open tasks'), default=0)

    @property
    def is_present(self):
        return not self.is_temporary and not self.is_released

    @property
    def is_temporary(self):
        if self.temporary_released_start and self.temporary_released_end:
            date = datetime.now().date()
            return self.temporary_released_start <= date <= self.temporary_released_end

    @property
    def is_released(self):
        if self.closed_since:
            date = datetime.now().date()
            return self.closed_since <= date

    def __str__(self):
        return self.file_id

    def save(self, *args, **kwargs):
        if not self.file_id:
            self.file_id = self._get_unique_file_id()
        return super().save(*args, **kwargs)

    def _get_unique_file_id(self):
        unique = get_random_string(length=6, allowed_chars='0123456789')
        while unique in self._meta.model.objects.values_list('patient_id', flat=True):
            unique = get_random_string(length=6, allowed_chars='0123456789')
        return unique


class ArchiveComment(TimeStampedModel):
    """
    ArchiveComment - comment on file in archive.
    """
    file = models.ForeignKey('File', verbose_name=_('File'), on_delete=models.CASCADE)
    comment = models.TextField(_('Comment'))
    user = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Archive Comment')
        verbose_name_plural = _('Archive Comments')
        db_table = 'archive_comment'
        ordering = ('-created',)


class EmergencyContact(TimeStampedModel):
    """
    EmergencyContact model stores information about patients emergency contacts.
    """
    patient = models.ForeignKey('Patient', verbose_name=_('File'), on_delete=models.CASCADE)
    relation = models.CharField(_('Relation'), choices=choices.RELATIONS, max_length=16, blank=True, null=True)
    name = models.CharField(_('Name'), max_length=128, blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=255, blank=True, null=True)
    trusted = models.BooleanField(_('Is trusted'), default=False)
    email = models.EmailField(_('E-mail Address'), max_length=128, blank=True, null=True)
    deleted = models.BooleanField(_('Deleted Contact'), default=False)
    reason = models.TextField(_('Reason for deletion'), null=True, blank=True)
    creator = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Emergency Contact')
        verbose_name_plural = _('Emergency Contacts')
        db_table = 'emergency_contacts'
        ordering = ('-created',)

    def __str__(self):
        return self.name
