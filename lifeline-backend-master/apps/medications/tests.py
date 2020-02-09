from rest_framework.test import APIClient
from django.test import TestCase

from apps.accounts.models import User
from apps.patients.models import Patient, File
from apps.units.models import Unit

from apps.medications.models import (
    MedicationCategory,
    Prescription,
    MedicationIntake,
    Drug,
    TimeSlot
)

from apps.medications.serializers import (
    MedicationIntakeSerializer
)

from .fixtures import (
    UNIT_1,
    DOCTOR_ACCOUNT_1,
    PATIENT_1,
    PATIENT_FILE_1,
    MEDICATION_CATEGORY_1,
    DRUG_1,
    PRESCRIPTION_1,
    TIME_SLOT_1,
    MEDICATION_INTAKES_LIST
)

C = APIClient()


class MedicationsTests(TestCase):
  def setUp(self):
    self.base_url = '/api/v1/medications'

    self.unit_1 = Unit.objects.create(**UNIT_1)
    self.doctor_1 = User.objects.create_superuser(
        DOCTOR_ACCOUNT_1['email'],
        DOCTOR_ACCOUNT_1['password']
    )
    self.doctor_1.units.add(self.unit_1)
    self.patient_1 = Patient.objects.create(**PATIENT_1)

    self.patient_file_1 = File.objects.create(**{
        **PATIENT_FILE_1,
        'patient': self.patient_1,
        'unit': self.unit_1
    })

    self.medication_category_1 = MedicationCategory.objects.create(**MEDICATION_CATEGORY_1)
    self.medication_drug_1 = Drug.objects.create(**{
        **DRUG_1, 
        'category': self.medication_category_1
    })

    self.prescription_1 = Prescription.objects.create(**{
        **PRESCRIPTION_1,
        'editor': self.doctor_1,
        'drug': self.medication_drug_1,
        'file': self.patient_file_1
    })

    self.time_slot_1 = TimeSlot.objects.create(**{
        **TIME_SLOT_1,
        'prescription': self.prescription_1
    })

    def create_intake(mock_intake):
      prescription = Prescription.objects.get(id=self.prescription_1.id)
      return MedicationIntake.objects.create(**{
          **mock_intake, 
          'prescription': prescription
      })

    self.medication_intakes = list(map(create_intake, MEDICATION_INTAKES_LIST))

    C.login(
        username=self.doctor_1.email,
        password=DOCTOR_ACCOUNT_1['password']
    )

  def test_intake_model(self):
    """ Check created `MedicationIntake` obj list from fixtures """
    self.assertEqual(len(MEDICATION_INTAKES_LIST), len(self.medication_intakes))

  def test_intake_serializer(self):
    """ Get data from `MedicationIntakeSerializer` """

    medication_intake_data_list = MedicationIntakeSerializer(
        self.medication_intakes, many=True).data
    self.assertEqual(len(medication_intake_data_list),
                     len(self.medication_intakes))

    # ensure data has timestamps
    def check_for_timestamps(intake):
      return isinstance(intake['time'], int)

    check_for_timestamps_result = list(
        map(check_for_timestamps, medication_intake_data_list))
    self.assertEqual(False not in check_for_timestamps_result, True)

  def test_endpoint_drugs(self):
      """ Test of `/api/v1/medications/drugs/` """
      query_params = '?search=p'
      url = self.base_url + '/drugs/' + query_params

      data = C.get(url).json()
      self.assertEqual(len(data), 1)

  def test_endpoint_medications(self):
      """ Test of `/api/v1/medications/` """
      patient_file_id = self.patient_file_1.id
      url = self.base_url + '/' + str(patient_file_id)

      data_1 = C.get(url).json()
      self.assertEqual(len(data_1), 1)

      data_payload = {
          "drug": self.medication_drug_1.id,
          "prescriptionType": "time-slots",
          "created": "2019-10-02T13:30:04.836316Z",
          "modified": "2019-10-02T13:30:04.836356Z",
          "mode": "DAILY",
          "meal": "BEFORE",
          "duration": "INDEF",
          "comment": "",
          "durationStart": "2019-10-02T16:20:38Z",
          "repeat": True,
          "repeatEvery": 1,
          "repeatReccurence": "DAYS",
          "cycle": True,
          "cycleEveryValue": 1,
          "cycleEveryReccurence": "WEEKS",
          "cycleOverValue": 1,
          "cycleOverReccurence": "MONTHS",
          'timeSlots': [
              {
                  'timeSlotType': 'step',
                  'timeStep': 1000,
                  'quantity': 1.25
              },
              {
                  'timeSlotType': 'step',
                  'timeStep': 2000,
                  'quantity': 2.25
              }
          ]
      }

      data_2 = C.post(url, data=data_payload, format='json').json()
      self.assertEqual(data_2['prescriptionType'], 'time-slots')
      self.assertEqual(len(data_2['timeSlots']), 2)
