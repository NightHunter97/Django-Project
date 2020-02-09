from lifeline.pagination import Pagination


class PatientFilePagination(Pagination):
    page_size = 16


class EmergencyContactPagination(Pagination):
    page_size = 12
