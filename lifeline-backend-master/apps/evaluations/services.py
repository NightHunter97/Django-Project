from apps.evaluations.models import Evaluation, Survey, Question, Answer


def get_all_evaluations():
    return Evaluation.objects.all()


def create_evaluation(data):
    return Evaluation.objects.create(**data)


def get_evaluation_count(file):
    return Evaluation.objects.filter(file=file).count()


def get_all_editable_evaluations():
    return Evaluation.objects.filter(survey_type__isnull=False)


def get_all_evaluations_for_file(file_id):
    return Evaluation.objects.filter(file__file_id=file_id)


def get_all_last_evaluations_for_file(file_id):
    return Evaluation.objects.filter(file__file_id=file_id).order_by('name', '-created').distinct('name')


def get_all_surveys():
    return Survey.objects.all()


def get_survey_by_survey_type(survey_id):
    return Survey.objects.filter(pk=survey_id).prefetch_related('questions', 'questions__answers').first()


def get_survey_question_by_pk(questions, key):
    if not key:
        return ''
    question = questions.filter(pk=key).first()
    return question.question if question else key


def get_question_answer(questions, key, value):
    if not key or not value:
        return ''
    question = questions.filter(pk=key).first()
    if not question:
        return ''
    if question.type != 'choice_filed':
        return value
    answer = question.answers.filter(pk=value).first()
    return answer.answer if answer else value


def get_survey_by_id(survey_id):
    return Survey.objects.filter(pk=survey_id).first()


def get_all_enabled_surveys():
    return Survey.objects.filter(is_active=True)


def get_enabled_surveys_for_user_groups(user):
    if user.is_superuser:
        return get_all_enabled_surveys()
    return get_all_enabled_surveys().filter(groups__in=user.groups.all())


def check_user_permissions(user, survey_id):
    return get_enabled_surveys_for_user_groups(user).filter(id=survey_id).exists()


def get_all_questions_in_survey(survey):
    return Question.objects.filter(survey=survey)


def get_all_answers_in_question(question):
    return Answer.objects.filter(question=question)

