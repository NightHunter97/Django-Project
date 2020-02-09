from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from apps.tasks.models import Schedule, Category, Task, RepeatedTask
import datetime
from dateutil import relativedelta


def get_all_tasks_by_file(file):
    return Schedule.objects.filter(file__file_id=file).order_by('task_id', 'prescription_id').distinct('task', 'prescription')


def get_all_scheduled_tasks():
    return Schedule.objects.prefetch_related('members', 'members__groups').select_related(
        'file', 'task', 'task__category', 'prescription__drug__category', 'creator'
    ).all()


def get_all_schedules():
    return Schedule.objects.select_related('file').all()


def get_today_schedules_for_units(units):
    return Schedule.objects.filter(
        status__isnull=True,
        date=datetime.datetime.today().date(),
        file__unit__in=units,
        file__closed_since__isnull=True
    ).count()


def get_my_schedules_for_units(units, user):
    return Schedule.objects.filter(
        status__isnull=True,
        date=datetime.datetime.today().date(),
        file__unit__in=units,
        file__closed_since__isnull=True,
        members=user
    ).count()


def get_due_schedules_for_units(units):
    return Schedule.objects.filter(
        status='STOP',
        file__unit__in=units,
        file__closed_since__isnull=True,
    ).count()


def get_filtered_periodic_tasks(periodic, file_id):
    return get_all_scheduled_tasks().filter(periodic=periodic, file__file_id=file_id)


def get_empty_schedules():
    return Schedule.objects.none()


def get_date_calendar_period(date):
    first_day = date.replace(day=1)
    next_date = first_day + relativedelta.relativedelta(months=1) + datetime.timedelta(days=7)
    prev_date = first_day - datetime.timedelta(days=7)
    return prev_date, next_date


def get_tasks_by_date(date, file_id):
    prev_date, next_date = get_date_calendar_period(date)
    return get_filtered_tasks_by_date(file_id, prev_date, next_date, True)


def get_medications_by_date(date, file_id):
    prev_date, next_date = get_date_calendar_period(date)
    return get_filtered_tasks_by_date(file_id, prev_date, next_date, False)


def get_filtered_tasks_by_date(file_id, prev_date, next_date, is_medicine):
    return get_all_scheduled_tasks().filter(
        Q(date__gte=f'{prev_date.strftime("%Y-%m-%d")}') & Q(date__lt=f'{next_date.strftime("%Y-%m-%d")}'),
        file__file_id=file_id, prescription__isnull=is_medicine
    )


def get_all_prescription_schedules(prescription):
    return Schedule.objects.filter(prescription=prescription)


def get_today_tasks(schedules, file_id):
    return [
        task for task in schedules
        if not task.file.is_released
        and not task.status
        and task.date == datetime.datetime.today().date()
        and task.file.pk == file_id
    ]


def get_open_and_due_tasks(file_id):
    return [
        task for task in get_all_scheduled_tasks().filter(
            Q(status__isnull=True) | Q(status='STOP'), file__file_id=file_id
        )
        if not task.file.is_released
    ]


def get_open_tasks(file_id):
    return get_all_scheduled_tasks().filter(
        date__gte=datetime.datetime.today().date(), file__file_id=file_id, status__isnull=True
    )


def get_expired_tasks(schedules, file_id):
    return [task for task in schedules if task.status == 'STOP' and task.file.id == file_id]


def get_all_categories():
    return Category.objects.all()


def get_all_tasks():
    return Task.objects.all()


def get_repeated_schedules(root_id):
    return Schedule.objects.filter(root_id=root_id)


def get_next_schedule(root_id, date, time):
    return Schedule.objects.filter(root_id=root_id).filter(Q(date__gt=date) | Q(date__gte=date, time__gt=time)).first()


def get_tasks_in_category(category_slug):
    return Task.objects.filter(category__slug=category_slug)


def get_task_by_id(task_id):
    return Task.objects.filter(id=task_id)


def get_schedule_by_id(pk):
    try:
        return Schedule.objects.get(id=pk)
    except ObjectDoesNotExist:
        return


def delete_all_future_tasks(root_id, date):
    return Schedule.objects.filter(root_id=root_id, date__gte=date).delete()


def tasks_root_update(data, tasks):
    if isinstance(tasks, list) and len(tasks) > 1:
        tasks_ids = [task.id for task in tasks]
        create_repeated_task(data, tasks_ids[0], tasks[0])
        if tasks_ids:
            Schedule.objects.filter(id__in=tasks_ids).update(root_id=tasks_ids[0])


def create_repeated_task(data, task_id, task):
    repeats = data.get('repeats')
    interval = data.get('interval')
    end_date = data.get('end_date')
    week_days = data.get('week_days') or []
    if len(week_days) > 0:
        week_days = [str(day) for day in week_days]
    times = data.get('times') or []
    RepeatedTask.objects.create(
        root_id=task_id, date=task.date, time=task.time, comment=task.comment, periodic=task.periodic,
        slot=task.slot, week_days=",".join(week_days), interval=interval, repeats=repeats, end_date=end_date,
        times=",".join(times)
    )


def delete_repeated_tasks(root_id):
    rep_task = RepeatedTask.objects.filter(root_id=root_id).first()
    if rep_task:
        rep_task.delete()


def delete_all_chained_tasks(root_id):
    if root_id:
        Schedule.objects.filter(root_id=root_id).delete()


def get_categories_for_user_groups(user):
    if user.is_superuser:
        return get_all_categories()
    return get_all_categories().filter(groups__in=user.groups.all())


def get_category_by_slug(slug):
    try:
        return Category.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return
