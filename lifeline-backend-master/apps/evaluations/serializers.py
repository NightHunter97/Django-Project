from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.accounts.serializers import UserSerializer
from apps.evaluations.models import Evaluation, Answer, Question, Survey
from apps.evaluations.services import get_survey_by_id, check_user_permissions
from apps.patients.services import get_file_by_file_id
from apps.utils.mixins import FileValidationMixin


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('id', 'answer', )


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    question_type = serializers.CharField(source='type')

    class Meta:
        model = Question
        fields = ('id', 'question', 'required', 'category', 'question_type', 'answers')


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    survey_results = serializers.DictField(required=False)
    evaluation_id = serializers.CharField(required=False)
    survey_name = serializers.CharField(source='name')

    class Meta:
        model = Survey
        fields = ('id', 'survey_name', 'questions', 'survey_results', 'evaluation_id')


class EvaluationsBaseSerializer(FileValidationMixin, serializers.ModelSerializer):
    survey_type = serializers.CharField(required=True)
    file = serializers.CharField(required=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evaluation
        fields = ('id', 'user', 'name', 'file', 'survey_results', 'is_editable', 'edited_by', 'survey_type')

    def create(self, validated_data):
        file_id = self.validated_data.get('file')
        file = get_file_by_file_id(file_id)
        survey_id = self.validated_data.get('survey_type')

        try:
            user = self.context.get('request')._user
        except AttributeError:
            user = None

        survey = None

        if survey_id:
            survey = get_survey_by_id(survey_id=int(survey_id))
        if not survey:
            raise ValidationError("Survey does not exist.")

        if not check_user_permissions(user, survey.id):
            raise ValidationError("No permission.")

        validated_data.update(
            {
                'survey_type': survey,
                'name': survey.pk,
                'file': file,
                'user': user
            }
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        try:
            user = self.context.get('request')._user
        except AttributeError:
            user = None

        if not check_user_permissions(user, instance.survey_type.id):
            raise ValidationError("No permission.")

        validated_data.update(
            {
                'file': instance.file,
                'survey_type': instance.survey_type,
                'edited_by': user
            }
        )
        return super().update(instance, validated_data)


class EvaluationsSerializer(EvaluationsBaseSerializer):
    name = serializers.CharField(read_only=True, source='survey_type')
    survey_results = serializers.SerializerMethodField()
    user = serializers.CharField(read_only=True)
    is_editable = serializers.SerializerMethodField()
    static_name = serializers.CharField(read_only=True, source='name')

    class Meta:
        model = Evaluation
        fields = ('id', 'user', 'created', 'is_editable',
                  'file', 'survey_results', 'name', 'static_name')

    def get_survey_results(self, obj):
        return obj.survey_results_display

    def get_is_editable(self, obj):
        try:
            user = self.context.get('request')._user
        except KeyError:
            return False
        if obj.survey_type and (check_user_permissions(user, obj.survey_type.id) or user.is_superuser):
            return True
        return False


class SurveyLightSerializer(serializers.ModelSerializer):
    survey_name = serializers.CharField(source='name')

    class Meta:
        model = Survey
        fields = ('survey_name', 'id')
