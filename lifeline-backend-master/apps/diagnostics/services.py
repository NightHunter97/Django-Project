from apps.diagnostics.models import DiagnosticFile, Diagnose, HealthScreening, Diagnostic


def get_diagnostic_file(id):
    return DiagnosticFile.objects.get(id=id)


def get_diagnostics_by_file(file_id):
    return Diagnostic.objects.filter(file__file_id=file_id)


def get_all_diagnoses():
    return Diagnose.objects.all()


def get_all_health_screening():
    return HealthScreening.objects.all()


def get_all_diagnositcs():
    return Diagnostic.objects.select_related('file', 'user', 'diagnose').all()
