from datetime import datetime, timedelta

from django.db.models import Q

from apps.tasks.models import Schedule
from lifeline.celery import app


@app.task
def expire_tasks():
    two_weeks_ago = datetime.now() - timedelta(days=14)
    expired = Schedule.objects.filter(date__lt=datetime.today().date(), status__isnull=True)
    for task in expired:
        task.status = 'STOP'
        task.save(update_fields=['status'])
    undone = Schedule.objects.filter(Q(status__isnull=True) | Q(status='STOP'), date__lt=two_weeks_ago)
    for task in undone:
        task.status = 'UNDN'
        task.save(update_fields=['status'])
    return {'expired': expired.count(), 'undone': undone.count()}
