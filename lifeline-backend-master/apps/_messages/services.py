from django.db.models import Q

from apps._messages.models import Message, AboutPatient


def get_empty_messages():
    return Message.objects.all()


def get_all_messages():
    return Message.objects.all()


def get_user_messages(user_id):
    return Message.objects.filter(Q(sender=user_id) | Q(receivers__uuid=user_id)).distinct()


def get_all_about_patient_messages():
    return AboutPatient.objects.all()


def get_about_patient_messages(user):
    return AboutPatient.objects.select_related('file__patient', 'user').filter(
        Q(file__unit__in=user.units.all()) & ~Q(hidden_for__contains=[user.uuid])
    )


def create_about_patient_message(subject_en, subject_fr, subject_nl, msg_content, file, user):
    return AboutPatient.objects.create(
        subject_en=subject_en,
        subject_fr=subject_fr,
        subject_nl=subject_nl,
        msg_content=msg_content,
        file=file,
        user=user
    )
