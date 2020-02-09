from unittest import mock

from django.test import Client, override_settings
from rest_framework.test import APITestCase


@override_settings(MIDDLEWARE=[])
class PatientsValidationTest(APITestCase):

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.patient_data = {
            'full_name': 'Joe Doe', 'card_number': '12234234', 'card_type': 'CHI', 'document_type': 'B_ID',
            'language': 'E', 'birth_date': '1912-01-01', 'gender': 'M', 'marital_status': 'SI',
            'partner_name': 'Partner', 'nationality': 'UKR', 'country': 'Ukraine', 'address': 'Bolivar st. 27',
            'post_code': '122133', 'national_register': 'test', 'foreign_register': 'test',
            'phone_number': '12312312313', 'email': 'test@test.com', 'is_vip': True, 'religion': 'ADV',
            'general_practitioner': 'test', 'death_date': '2001-01-01', 'note': 'test', 'insurance_policy': '101',
            'policy_holder': 'test', 'validity_end': '2000-01-01', 'beneficiary_id': 'test',
            'beneficiary_occupation': 'PH', 'heading_code': '7', 'is_employed': True, 'dependants': 'NO',
            'is_third_party_auth': True, 'disability_recognition': True, 'regional_recognition': True,
            'disability_assessment_points': 'test', 'income_origin': 'WRK', 'income_amount': 'test', 'expenses': 'test',
            'debts': True, 'attorney': True, 'management': 'test', 'admission': 'ISO', 'occupation': 'test',
            'career': 'test', 'education': 'NM', 'edu_pathway': 'PR'
        }

    @mock.patch('apps.patients.views.PatientsViewSet._mutate_request_data', mock.Mock())
    @mock.patch('apps.patients.serializers.does_email_exist')
    @mock.patch('apps.patients.views.LifeLinePermissions.has_permission')
    @mock.patch('rest_framework.permissions.IsAuthenticated.has_permission')
    def test_patient_info_valid_ok(self, has_permission, life_line_permissions, does_email_exist):
        does_email_exist.return_value = False
        has_permission.return_value = True
        life_line_permissions.return_value = True
        c = Client()
        response = c.post('/api/v1/patients/', self.patient_data, **{'HTTP_VALIDATION': 'true'})
        self.assertEqual(response.data, {'Data': 'Valid'})
        self.assertEqual(response.status_code, 200)

    @mock.patch('apps.patients.views.PatientsViewSet._mutate_request_data', mock.Mock())
    @mock.patch('apps.patients.views.LifeLinePermissions.has_permission')
    @mock.patch('rest_framework.permissions.IsAuthenticated.has_permission')
    def test_validate_required_fields_fail(self, is_authenticated, life_line_permissions):
        is_authenticated.return_value = True
        life_line_permissions.return_value = True
        self.patient_data.update({
            'full_name': '',
            'card_number': '',
            'card_type': '',
            'document_type': '',
            'language': '',
            'birth_date': '',
            'gender': '',
            'marital_status': '',
            'partner_name': '',
            'nationality': '',
            'address': '',
            'country': '',
            'post_code': '',
            'national_register': '',
            'foreign_register': '',
            'phone_number': '',
            'email': '',
            'religion': '',
            'general_practitioner': ''
        })
        c = Client()
        response = c.post('/api/v1/patients/', self.patient_data, **{'HTTP_VALIDATION': 'true'})
        self.assertEqual(str(response.data['full_name'][0]), 'This field may not be blank.')
        self.assertEqual(str(response.data['birth_date'][0]), 'This field may not be blank.')
        self.assertEqual(str(response.data['gender'][0]), 'This field may not be blank.')
        self.assertEqual(response.status_code, 400)
