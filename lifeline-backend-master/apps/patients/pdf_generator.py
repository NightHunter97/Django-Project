from datetime import datetime

from apps.patients.services import get_patients_for_export, vitals_to_table
from apps.reports.services import get_report_logo
from apps.utils.pdf_generator import PDFBaseGenerator


class PDFPatientGenerator(PDFBaseGenerator):
    template_path = 'patients/patient_export_template.html'

    def get_context(self):
        """Context data for pdf template"""
        patient = get_patients_for_export(patient_id=self.object_id)
        if not patient:
            return {}
        headers = (
            "Date", "Blood Pressure",
            "Pulse", "Height", "Temp",
            "Blood Sugar", "Weight", "Saturation",
            "Breathing Rate"
        )
        vitals = vitals_to_table(patient.files.all())
        return {
            'logo': get_report_logo(),
            'patient': patient,
            'files': patient.files,
            'headers': headers,
            'file_to_vitals': vitals,
            'emergency_contact': patient.emergencycontact_set,
            'export_date': datetime.today()
        }
