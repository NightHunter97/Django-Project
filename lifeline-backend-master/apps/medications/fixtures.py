UNIT_1 = {
    'name': 'unit:1',
    'beds': 4
}

DOCTOR_ACCOUNT_1 = {
    'email': 'incerta.test.one@gmail.com',
    'password': '1234Qwer!'
}

PATIENT_1 = {
    'full_name': 'Joe Doe'
}

PATIENT_FILE_1 = {
    'file_id': '1'
}

MEDICATION_CATEGORY_1 = {
    'term': 'medication_category:1'
}

PRESCRIPTION_1 = {
    "created": "2019-10-02T13:30:04.836316Z",
    "modified": "2019-10-02T13:30:04.836356Z",
    "mode": "DAILY",
    "meal": "BEFORE",
    "prescription_type": "time-slots",
    "duration": "INDEF",
    "comment": "",
    "duration_start": "2019-10-02T16:20:38Z",
    "repeat": True,
    "repeat_every": 1,
    "repeat_reccurence": "DAYS",
    "cycle": True,
    "cycle_every_value": 1,
    "cycle_every_reccurence": "WEEKS",
    "cycle_over_value": 1,
    "cycle_over_reccurence": "MONTHS",
}

TIME_SLOT_1 = {
    'time_slot_type': 'step',
    'time_step': 1000 * 60 * 60 * 6, # 6 hours,
    'quantity': 1.25
}

DRUG_1 = {
    'name': 'Paracetamol 30mg'
}

MEDICATION_INTAKE_1 = {
    'prescription': 1,
    'comment': 'comment:1',
    'time': '2000-01-01T00:00+0300',
    'quantity': 1
}

MEDICATION_INTAKE_2 = {
    'prescription': 1,
    'comment': 'comment:2',
    'time': '2000-01-01T01:00+0300',
    'quantity': 1
}

MEDICATION_INTAKES_LIST = [MEDICATION_INTAKE_1, MEDICATION_INTAKE_2]
