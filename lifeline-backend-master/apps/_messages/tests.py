from unittest import mock
from django.test import Client, SimpleTestCase
from rest_framework import status
from rest_framework.response import Response

from apps._messages.serializers import MessageSerializer


class MessagesViewSetTest(SimpleTestCase):
    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_create_message_unauthorized(self):
        c = Client()
        response = c.post('/api/v1/messages/', {})
        self.assertEqual(response.status_code, 401)

    @mock.patch('rest_framework.mixins.CreateModelMixin.create')
    @mock.patch('apps.patients.views.LifeLinePermissions.has_permission')
    @mock.patch('rest_framework.permissions.IsAuthenticated.has_permission')
    def test_create_message(self, has_permission, lifeline_permission, create):
        create.return_value = Response({}, status=status.HTTP_201_CREATED)
        has_permission.return_value = True
        lifeline_permission.return_value = True
        c = Client()
        response = c.post('/api/v1/messages/', {})
        self.assertEqual(response.status_code, 201)

    @mock.patch('rest_framework.relations.PrimaryKeyRelatedField.to_internal_value', mock.Mock())
    def test_validation_create_message(self):
        message_data = {
            'subject': 'Test subject',
            'msg_content': 'Message content',
            'receivers': ['c60d1a5f-c835-4771-b9a9-85361fafe719']
        }
        expected_result = {
            'subject': 'Test subject',
            'msg_content': 'Message content',
            'receivers': [mock.ANY]
        }

        serializer = MessageSerializer(data=message_data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, expected_result)

        serializer = MessageSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['subject'][0].code, 'required')
        self.assertEqual(serializer.errors['msg_content'][0].code, 'required')
        self.assertEqual(serializer.errors['receivers'][0].code, 'required')

    @mock.patch('apps.utils.mixins.DestroyDataMixin.destroy')
    @mock.patch('apps.patients.views.LifeLinePermissions.has_permission')
    @mock.patch('rest_framework.permissions.IsAuthenticated.has_permission')
    def test_delete_message(self, has_permission, lifeline_permission, destroy):
        has_permission.return_value = True
        lifeline_permission.return_value = True
        destroy.return_value = Response({"id": 1}, status=status.HTTP_200_OK)
        c = Client()
        response = c.delete('/api/v1/messages/1/', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"id": 1})
