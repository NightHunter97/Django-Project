from apps.diagnostics.reader import XslxReader
from apps.diagnostics.services import get_diagnostic_file
from lifeline.celery import app


@app.task
def file_parsing(pk, type):
    diagnostic_file = get_diagnostic_file(pk)
    reader = XslxReader(diagnostic_file)
    getattr(reader, type)()
