from django.contrib import admin

from apps.accounts.mixins import AdminLogMixin
from apps.evaluations.forms import QuestionForm, AddGroupSurveyForm
from apps.evaluations.models import Evaluation, Survey, Question, Answer
from django.utils.translation import ugettext_lazy as _


class QuestionInline(admin.TabularInline):
    model = Question
    ordering = ('id',)
    extra = 0

    fieldsets = (
        ('Question', {
            'fields': (
                'required', 'category', 'question_en', 'question_fr', 'question_nl', 'type',
            )
        }),
    )


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

    fieldsets = (
        ('Answers', {
            'fields': (
                'answer_en', 'answer_fr', 'answer_nl',
            )
        }),
    )


@admin.register(Evaluation)
class EvaluationAdmin(AdminLogMixin, admin.ModelAdmin):
    readonly_fields = ('user', 'created', 'survey_type',
                       'survey_results', 'name',
                       'static_results_en', 'static_results_fr', 'static_results_nl', 'file',
                       'created', 'modified', 'is_editable')
    icon = '<i class="material-icons">thumbs_up_down</i>'
    list_display = ('evaluation_name', '__str__', 'user', 'created', 'is_editable')

    fieldsets = (
        ('Evaluations', {
            'fields': (
                'name', 'file', 'user', 'survey_type', 'survey_results', 'static_results_en',
                'static_results_fr', 'static_results_nl', 'edited_by', 'created', 'modified', 'is_editable'
            )
        }),
    )

    def evaluation_name(self, evaluation):
        return evaluation.survey_type or evaluation.name

    evaluation_name.allow_tags = True
    evaluation_name.short_description = _('Evaluation Name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'file', 'file__patient', 'survey_type')

    def has_add_permission(self, request):
        return False


@admin.register(Survey)
class SurveyAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">thumbs_up_down</i>'
    list_display = ('__str__', 'is_active')
    form = AddGroupSurveyForm
    ordering = ('-id',)

    search_fields = ('name', )

    fieldsets = (
        ('Survey INFO', {
            'fields': ('name_en', 'name_fr', 'name_nl', 'is_active', 'groups')
        }),
    )

    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">thumbs_up_down</i>'
    list_display = ('survey', 'question', 'category', 'type', 'required')
    list_filter = ('survey', )
    ordering = ('-id',)
    form = QuestionForm
    search_fields = ('survey', 'question')

    class Media:
        js = ('evaluations/js/answers-formset.js', )

    fieldsets = (
        ('Question INFO', {
            'fields': (
                'survey', 'required', 'category', 'question_en', 'question_fr', 'question_nl', 'type',
            )
        }),
    )

    inlines = [AnswerInline]
