ACTIVITIES = [
    {
        'path': r'^/api/v1/patients/files/[0-9]{6}/$',
        'info': 'View file',
        'code': 200,
        'method': 'GET',
        'file_index': 5,
        'file_data': ''
    },
    # tasks
    {
        'path': r'^/api/v1/tasks/[0-9]*/$',
        'info': 'Task was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/tasks/$',
        'info': 'Task was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/tasks/[0-9]*/$',
        'info': 'Task was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # patient
    {
        'path': r'^/api/v1/patients/$',
        'info': 'Patient was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': ''
    },
    {
        'path': r'^/api/v1/patients/[0-9]*/$',
        'info': 'Patient was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': ''
    },
    {
        'path': r'^/api/v1/patients/status/[0-9]*/$',
        'info': 'Patient file status was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # vitals
    {
        'path': r'^/api/v1/vitals/$',
        'info': 'Vital params were created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/vitals/[0-9]*/$',
        'info': 'Vital param was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/vitals/[0-9]*/$',
        'info': 'Vital param was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # wounds
    {
        'path': r'^/api/v1/wounds/$',
        'info': 'Wound was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/wounds/[0-9]*/$',
        'info': 'Wound was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/wounds/[0-9]*/$',
        'info': 'Wound was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # medications
    {
        'path': r'^/api/v1/medications/$',
        'info': 'Medication was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/medications/[0-9]*/$',
        'info': 'Medication was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/medications/[0-9]*/$',
        'info': 'Medication was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # diagnostics
    {
        'path': r'^/api/v1/diagnostics/$',
        'info': 'Diagnostic was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/diagnostics/[0-9]*/$',
        'info': 'Diagnostic was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/diagnostics/[0-9]*/$',
        'info': 'Diagnostic was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # journal
    {
        'path': r'^/api/v1/journal/$',
        'info': 'Journal comment was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/journal/[0-9]*/$',
        'info': 'Journal comment was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/journal/[0-9]*/$',
        'info': 'Journal comment was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # emergency contacts
    {
        'path': r'^/api/v1/patients/emergency/$',
        'info': 'Emergency contact was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/patients/emergency/[0-9]*/$',
        'info': 'Emergency contact was changed',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/patients/emergency/[0-9]*/$',
        'info': 'Emergency contact was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # reports
    {
        'path': r'^/api/v1/reports/$',
        'info': 'Report File was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    {
        'path': r'^/api/v1/reports/visualize/$',
        'info': 'Report File was visualized',
        'code': 200,
        'method': 'POST',
        'file_index': 0,
        'file_data': 'activity_file_id'
    },
    # messages
    {
        'path': r'^/api/v1/messages/about/[0-9]*/$',
        'info': 'About patient message was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': ''
    },
    {
        'path': r'^/api/v1/messages/about/[0-9]*/$',
        'info': 'About message was read',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': ''
    },
    {
        'path': r'^/api/v1/messages/$',
        'info': 'Team message was created',
        'code': 201,
        'method': 'POST',
        'file_index': 0,
        'file_data': ''
    },
    {
        'path': r'^/api/v1/messages/[0-9]*/$',
        'info': 'Team message was deleted',
        'code': 200,
        'method': 'DELETE',
        'file_index': 0,
        'file_data': ''
    },
    {
        'path': r'^/api/v1/messages/[0-9]*/$',
        'info': 'Team message was read',
        'code': 200,
        'method': 'PATCH',
        'file_index': 0,
        'file_data': ''
    },
]
