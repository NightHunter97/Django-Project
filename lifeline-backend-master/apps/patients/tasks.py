from apps.patients.pdf_generator import PDFPatientGenerator
from apps.patients.services import get_file_by_pk
from apps.tasks.services import get_all_schedules
from lifeline.celery import app


@app.task
def invalidate_patient_task_count(file_pk):
    file = get_file_by_pk(file_pk)
    file.open_tasks = len([
        task for task in get_all_schedules()
        if task.file.pk == file_pk and not task.status
    ])
    file.due_tasks = len([
        task for task in get_all_schedules()
        if task.status == 'STOP' and task.file.pk == file_pk
    ])

    file.save(update_fields=['open_tasks', 'due_tasks'])


@app.task
def patient_generate_export_file(patient_id, owner):
    PDFPatientGenerator(prefix='patient', object_id=patient_id, owner=owner).proceed()
