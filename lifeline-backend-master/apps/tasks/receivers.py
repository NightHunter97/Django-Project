from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from apps.patients.tasks import invalidate_patient_task_count
from apps.tasks.models import Schedule
from apps.tasks.services import delete_repeated_tasks


@receiver(post_delete, sender=Schedule)
def delete_config(sender, instance, **kwargs):
    if not Schedule.objects.filter(root_id=instance.root_id).exists():
        delete_repeated_tasks(instance.root_id)


@receiver([post_delete, post_save], sender=Schedule)
def invalidate_tasks_count(sender, instance, **kwargs):
    if not cache.get(f'invalidate_patient_task_count_{instance.file.pk}'):
        invalidate_patient_task_count.apply_async((instance.file.pk,), countdown=10)
    cache.set(f'invalidate_patient_task_count_{instance.file.pk}', True, 10)
