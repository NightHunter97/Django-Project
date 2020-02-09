from apps.accounts.models import Activity
from apps.patients.services import get_file_by_file_id, get_patient
from lifeline.celery import app


@app.task
def user_activity_track(username, email, activity, file_id, patient_id, data):
    file = get_file_by_file_id(file_id)
    patient = get_patient(patient_id)

    if file:
        patient = file.patient
    elif patient:
        patient = patient
    Activity.objects.create(
        user=username,
        email=email,
        activity=activity,
        patient=patient,
        patient_id=getattr(patient, 'patient_id', None),
        file_id=file,
        data=data
    )
