from datetime import datetime

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.medications.serializers import PrescriptionLightSerializer
from apps.tasks.mixins import LocalStaticServe
from apps.tasks.models import Schedule, Task, Category, RepeatedTask
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.templatetags.staticfiles import static

from apps.tasks.services import get_task_by_id


class TaskSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'name', 'slug')


class CategorySerializer(LocalStaticServe, serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('slug', 'name', 'icon')

    def get_icon(self, obj):
        if obj.icon:
            return static(obj.icon) if not self._is_local() else self._get_local_static_file(static(obj.icon))
        if obj.image:
            return obj.image.url


class ScheduleSerializer(LocalStaticServe, serializers.ModelSerializer):
    patch_fields = ('date', 'members', 'comment', 'status', 'end_date', 'periodic', 'time')
    root_id = serializers.CharField(required=False, allow_null=True)
    initial_object = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    task_id = serializers.CharField(write_only=True, allow_null=True)
    left = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    mode = serializers.SerializerMethodField()
    periodic = serializers.CharField(required=False, write_only=True)
    users = serializers.SerializerMethodField()
    slot = serializers.BooleanField(required=False)
    end_time = serializers.SerializerMethodField()
    file_id = serializers.CharField(source='file.file_id', read_only=True)
    team_members = serializers.SerializerMethodField()
    user = UserSerializer(source='creator', read_only=True)
    icon = serializers.SerializerMethodField()
    all_members = None
    repeated_schedule = None

    class Meta:
        model = Schedule
        fields = (
            'date',
            'time',
            'comment',
            'status',
            'task',
            'task_id',
            'members',
            'file',
            'file_id',
            'id',
            'root_id',
            'left',
            'next',
            'mode',
            'periodic',
            'users',
            'slot',
            'end_time',
            'wound',
            'team_members',
            'prescription',
            'creator',
            'user',
            'initial_object',
            'icon'
        )

    def get_icon(self, schedule):
        file = self.get_icon_file(schedule)
        if not file:
            default = static('tasks/icons/no-icon.png')
            return default if not self._is_local() else self._get_local_static_file(default)
        return file.replace('.svg', '-white.svg')

    def get_icon_file(self, obj):
        if obj.prescription:
            return static('tasks/icons/medication.svg')\
                if not self._is_local() else self._get_local_static_file(static("tasks/icons/medication.svg"))
        if obj.task and obj.task.category and obj.task.category.icon:
            return static(obj.task.category.icon) \
                if not self._is_local() else self._get_local_static_file(static(obj.task.category.icon))
        if obj.task and obj.task.category and obj.task.category.image:
            return obj.task.category.image.url

    def get_task(self, obj):
        if not obj.task and obj.prescription:
            return PrescriptionLightSerializer(instance=obj.prescription).data
        return TaskSerializer(instance=obj.task).data

    def get_team_members(self, obj):
        return UserSerializer(obj.members.all(), many=True).data

    def validate_task_id(self, value):
        if value:
            task = get_task_by_id(value)
            if not task:
                raise serializers.ValidationError(_('Task id is not present in table "task"'))
        return value

    def get_end_time(self, obj):
        if obj.slot and obj.time:
            return f'{obj.time.hour + 2}:00:00'

    def get_users(self, obj):
        if not self.all_members:
            self.all_members = [(user.username, user.groups.first()) for user in obj.members.all()]
        return [
            f'{username}({group.name if group else _("No group")})'
            for username, group in self.all_members
        ]

    def get_left(self, obj):
        if obj.root_id:
            tasks = [task for task in self._kwargs['context']['_cached__schedules'] if task.root_id == obj.root_id]
            return len([task for task in tasks if datetime.combine(task.date, task.time) > datetime.now()])

    def get_next(self, obj):
        if obj.root_id:
            tasks = [
                task for task in self._kwargs['context']['_cached__schedules']
                if task.root_id == obj.root_id and datetime.combine(task.date, task.time) > datetime.combine(obj.date, obj.time)
            ]
            return datetime.strftime(tasks[0].date, '%d %b, %Y') if tasks else None

    def get_initial_object(self, obj):
        if obj.root_id:
            if not self.repeated_schedule:
                self.repeated_schedule = RepeatedTask.objects.filter(root_id=obj.root_id).first()
            if self.repeated_schedule:
                initial_data = {
                    'date': self.repeated_schedule.date,
                    'time': self.repeated_schedule.time,
                    'comment': self.repeated_schedule.comment,
                    'periodic': self.repeated_schedule.periodic,
                    'slot': self.repeated_schedule.slot,
                    'week_days': self.repeated_schedule.week_days,
                    'interval': self.repeated_schedule.interval,
                    'repeats': self.repeated_schedule.repeats,
                    'end_date': self.repeated_schedule.end_date,
                    'times': self.repeated_schedule.times
                }
                return initial_data

    def get_mode(self, obj):
        return obj.get_periodic_display()

    def update(self, instance, validated_data):
        validated_data = {
            field: validated_data[field] for field in self.patch_fields if validated_data.get(field) is not None
            }
        return super().update(instance, validated_data)
