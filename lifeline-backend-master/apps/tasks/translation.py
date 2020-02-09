from modeltranslation.translator import translator, TranslationOptions

from apps.tasks.models import Category, Task


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en',)


class TaskTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en',)


translator.register(Category, CategoryTranslationOptions)
translator.register(Task, TaskTranslationOptions)
