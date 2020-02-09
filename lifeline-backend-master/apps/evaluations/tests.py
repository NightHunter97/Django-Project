import json

from django.contrib.auth.models import Group, Permission
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.evaluations.models import Survey, Question, Answer, Evaluation
from apps.patients.models import File, Patient


@override_settings(MIDDLEWARE=[])
class ViewsTest(APITestCase):

    def tearDown(self):
        self.client.force_authenticate(user=None)

    @classmethod
    def setUpTestData(cls):
        cls.survey = Survey.objects.create(name='TestSurvey', is_active=True)
        cls.inactive_survey = Survey.objects.create(name='TestInactiveSurvey', is_active=False)
        cls.questions = []
        for i in range(5):
            question = Question.objects.create(
                survey=cls.survey,
                required=True,
                category=f'TestCategory {i}',
                question=f'TestQuestion {i}',
                type='choice_filed'
            )
            for j in range(3):
                Answer.objects.create(
                    answer=f'TestAnswer {j}',
                    question=question
                )
            cls.questions.append(question)

        cls.results = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '1',
            '5': '2'
        }
        cls.patient = Patient.objects.create(patient_id=21234)
        cls.file = File.objects.create(file_id='1', patient=cls.patient)

        cls.evaluation = Evaluation.objects.create(
            name=cls.survey.pk,
            file=cls.file,
            survey_results=cls.results,
            survey_type=cls.survey
        )

        cls.old_evaluation = Evaluation.objects.create(
            name='OldEval',
            file=cls.file,
            survey_type=None,
            static_results='[]',
            is_editable=False
        )

        cls.super_user = User.objects.create_superuser(
            email="test@superuser.ro",
            password="123qaz123!A"
        )

        cls.user = User.objects.create_user(
            username='TestUser',
            password="pass",
            language='en',
            email='test@test.com'
        )

        cls.limited_user = User.objects.create_user(
            username='TestUser2',
            password="pass",
            language='en',
            email='test2@test.com',
            is_staff=True
        )

        cls.group = Group.objects.filter(pk=1).first()
        for perm in Permission.objects.all():
            cls.group.permissions.add(perm)
        cls.limited_user.groups.add(cls.group)
        cls.survey.groups.add(cls.group)

    def test_get_meta_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.get('/api/v1/evaluations/meta/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Survey.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('id'), self.survey.pk)
        self.assertEqual(len(response.data[0].keys()), 2)

    def test_survey_view_list_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.get('/api/v1/evaluations/survey/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('id'), self.survey.pk)
        self.assertEqual(len(response.data[0].keys()), 2)

    def test_survey_view_list_archive_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        evaluation = Evaluation.objects.create(name="StaticCatTest", file=self.file, is_editable=False, survey_type=None)
        evaluation2 = Evaluation.objects.create(name="StaticCatTest2", file=self.file, is_editable=False, survey_type=None)

        response = self.client.get('/api/v1/evaluations/survey/?file=1&archive=true')
        old_evals = list(Evaluation.objects.filter(is_editable=False).values_list('name', flat=True))
        old_evals.append(self.inactive_survey.name)
        res = [
            value.get('survey_name')
            for value in response.data
            if value.get('survey_name') in old_evals
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(res), Evaluation.objects.filter(is_editable=False).count() + 1)
        evaluation.delete()
        evaluation2.delete()
        self.evaluation = Evaluation.objects.create(
            name=self.survey.pk,
            file=self.file,
            survey_results=self.results,
            survey_type=self.survey
        )

    def test_survey_view_retrieve_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.get(f'/api/v1/evaluations/survey/{self.survey.pk}/')

        self.assertEqual(response .status_code, 200)
        self.assertEqual(response.data.get('id'), self.survey.pk)
        self.assertEqual(len(response.data.keys()), 3)
        self.assertEqual(len(response.data.get('questions')), 5)
        self.assertEqual(len(response.data.get('questions')[0].get('answers')), 3)

    def test_survey_view_list_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/evaluations/survey/')

        self.assertEqual(response.status_code, 403)

    def test_survey_view_list_archive_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/evaluations/survey/?file=1&archive=true')

        self.assertEqual(response.status_code, 403)

    def test_survey_view_retrieve_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/v1/evaluations/survey/{self.survey.pk}/')

        self.assertEqual(response.status_code, 403)

    def test_get_meta_limited(self):
        self.client.force_authenticate(user=self.limited_user)

        new_active_survey = Survey.objects.create(name='TestSurvey2', is_active=True)

        response = self.client.get('/api/v1/evaluations/meta/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Survey.objects.count(), 3)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('id'), self.survey.pk)
        self.assertEqual(len(response.data[0].keys()), 2)
        new_active_survey.delete()

    def test_survey_view_list_limited(self):
        self.client.force_authenticate(user=self.limited_user)

        new_active_survey = Survey.objects.create(name='TestSurvey2', is_active=True)

        response = self.client.get('/api/v1/evaluations/survey/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get('id'), self.survey.pk)
        self.assertEqual(len(response.data[0].keys()), 2)
        new_active_survey.delete()
    
    def test_survey_view_retrieve_limited(self):
        self.client.force_authenticate(user=self.limited_user)

        new_active_survey = Survey.objects.create(name='TestSurvey2', is_active=True)

        response = self.client.get(f'/api/v1/evaluations/survey/{new_active_survey.pk}/')

        self.assertEqual(response.status_code, 404)

        response = self.client.get(f'/api/v1/evaluations/survey/{self.survey.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), self.survey.pk)
        self.assertEqual(len(response.data.keys()), 3)
        new_active_survey.delete()

    def test_list_evaluations_active_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.get(f'/api/v1/evaluations/?file={self.file.file_id}&survey_type={self.survey.pk}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), self.evaluation.pk)

    def test_list_evaluations_archive_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.get(f'/api/v1/evaluations/?file={self.file.file_id}&survey_type={self.old_evaluation.name}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), self.old_evaluation.pk)

    def test_retrieve_evaluation_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.get(f'/api/v1/evaluations/{self.evaluation.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), self.evaluation.pk)
        self.assertEqual(response.data.get('survey_results'), self.evaluation.survey_results_display)

    def test_retrieve_evaluation_for_edit_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.get(f'/api/v1/evaluations/{self.evaluation.pk}/?is_edit=true')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.data.get('id')), self.evaluation.survey_type.pk)
        self.assertEqual(int(response.data.get('evaluation_id')), self.evaluation.pk)
        self.assertEqual(response.data.get('survey_results'), self.evaluation.survey_results)

    def test_post_evaluation_superuser(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            'activity_file_id': self.file.file_id,
            'file': self.file.file_id,
            'survey_results': self.results,
            'survey_type': self.evaluation.survey_type.pk
        }

        response = self.client.post('/api/v1/evaluations/', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data.get('id'))
        self.assertEqual(response.data.get('file'), self.file.file_id)
        self.assertEqual(response.data.get('survey_results'), self.results)
        self.evaluation = Evaluation.objects.filter(is_editable=True).first()

    def test_list_evaluations_active_limited_user(self):
        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(f'/api/v1/evaluations/?file={self.file.file_id}&survey_type={self.survey.pk}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), self.evaluation.pk)

    def test_list_evaluations_archive_limited_user(self):
        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(f'/api/v1/evaluations/?file={self.file.file_id}&survey_type={self.old_evaluation.name}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), self.old_evaluation.pk)

    def test_retrieve_evaluation_limited_user(self):
        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(f'/api/v1/evaluations/{self.evaluation.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), self.evaluation.pk)
        self.assertEqual(response.data.get('survey_results'), self.evaluation.survey_results_display)

    def test_retrieve_evaluation_for_edit_limited_user(self):
        self.client.force_authenticate(user=self.limited_user)

        new_active_survey = Survey.objects.create(name='TestSurvey2', is_active=True)
        new_evaluation = Evaluation.objects.create(
            name=new_active_survey.pk,
            file=self.file,
            survey_results=self.results,
            survey_type=new_active_survey
        )

        response = self.client.get(f'/api/v1/evaluations/{new_evaluation.pk}/?is_edit=true')

        self.assertEqual(response.status_code, 404)

        response = self.client.get(f'/api/v1/evaluations/{self.evaluation.pk}/?is_edit=true')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.data.get('id')), self.evaluation.survey_type.pk)
        self.assertEqual(int(response.data.get('evaluation_id')), self.evaluation.pk)
        self.assertEqual(response.data.get('survey_results'), self.evaluation.survey_results)

    def test_post_evaluation_limited_user(self):
        self.client.force_authenticate(user=self.limited_user)

        data = {
            'activity_file_id': self.file.file_id,
            'file': self.file.file_id,
            'survey_results': self.results,
            'survey_type': self.evaluation.survey_type.pk
        }

        response = self.client.post('/api/v1/evaluations/', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data.get('id'))
        self.assertEqual(response.data.get('file'), self.file.file_id)
        self.assertEqual(response.data.get('survey_results'), self.results)
        self.evaluation = Evaluation.objects.filter(is_editable=True).first()

    def test_list_evaluations_active_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/v1/evaluations/?file={self.file.file_id}&survey_type={self.survey.pk}')

        self.assertEqual(response.status_code, 403)

    def test_list_evaluations_archive_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/v1/evaluations/?file={self.file.file_id}&survey_type={self.old_evaluation.name}')

        self.assertEqual(response.status_code, 403)

    def test_retrieve_evaluation_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/v1/evaluations/{self.evaluation.pk}/')

        self.assertEqual(response.status_code, 403)

    def test_retrieve_evaluation_for_edit_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/v1/evaluations/{self.evaluation.pk}/?is_edit=true')

        self.assertEqual(response.status_code, 403)

    def test_post_evaluation_no_permissions(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'activity_file_id': self.file.file_id,
            'file': self.file.file_id,
            'survey_results': self.results,
            'survey_type': self.evaluation.survey_type.pk
        }

        response = self.client.post('/api/v1/evaluations/', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 403)


class SignalsTest(APITestCase):

    def tearDown(self):
        Patient.objects.all().delete()
        Survey.objects.all().delete()
        self.survey = None
        self.evaluation = None
        self.file = None

    def setUp(self):
        self.survey = Survey.objects.create(name='TestSurvey', is_active=True)
        for i in range(5):
            question = Question.objects.create(
                survey=self.survey,
                required=True,
                category=f'TestCategory {i}',
                question=f'TestQuestion {i}',
                type='choice_filed'
            )
            for j in range(3):
                Answer.objects.create(
                    answer=f'TestAnswer {j}',
                    question=question
                )

        self.results = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '1',
            '5': '2'
        }
        patient = Patient.objects.create(patient_id=21234)
        self.file = File.objects.create(file_id=1, patient=patient)

        self.evaluation = Evaluation.objects.create(
            name=self.survey.pk,
            file=self.file,
            survey_results=self.results,
            survey_type=self.survey
        )

    def test_survey_modification(self):
        self.assertTrue(self.evaluation.is_editable)
        self.survey.name = "mod"
        self.survey.save()
        evaluation = Evaluation.objects.get(pk=self.evaluation.pk)
        self.assertFalse(evaluation.is_editable)

    def test_survey_modification_no_impact(self):
        self.assertTrue(self.evaluation.is_editable)
        group = Group.objects.first()
        self.survey.groups.add(group)
        evaluation = Evaluation.objects.get(pk=self.evaluation.pk)
        self.assertTrue(evaluation.is_editable)

    def test_question_modification(self):
        self.assertTrue(self.evaluation.is_editable)
        self.survey.questions.first().question = "mod"
        self.survey.questions.first().save()
        evaluation = Evaluation.objects.get(pk=self.evaluation.pk)
        self.assertFalse(evaluation.is_editable)

    def test_answer_modification(self):
        self.assertTrue(self.evaluation.is_editable)
        self.survey.questions.first().answers.first().answer = "mod"
        self.survey.questions.first().answers.first().save()
        evaluation = Evaluation.objects.get(pk=self.evaluation.pk)
        self.assertFalse(evaluation.is_editable)

    def test_new_evaluation(self):
        self.assertTrue(self.evaluation.is_editable)
        new_evaluation = Evaluation.objects.create(
            name=self.survey.pk,
            file=self.file,
            survey_results=self.results,
            survey_type=Survey.objects.get(pk=self.survey.pk)
        )
        evaluation = Evaluation.objects.get(pk=self.evaluation.pk)
        self.assertFalse(evaluation.is_editable)
        self.assertTrue(new_evaluation.is_editable)

    def test_results_to_static(self):
        display = self.evaluation.survey_results_display
        self.survey.name = "mod"
        self.survey.save()
        evaluation = Evaluation.objects.get(pk=self.evaluation.pk)
        static_display = evaluation.survey_results_display
        self.assertEqual(display, static_display)
