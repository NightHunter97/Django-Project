import xml.etree.ElementTree as Tree

from django.utils import translation

from apps.accounts.choices import SEX
from apps.patients.choices import COUNTRIES


def get_documents(content):
    root = Tree.fromstring(content)
    documents = {}
    for body in root[1]:
        for RegistryObjectList in body:
            for ExtrinsicObject in RegistryObjectList:
                doc_name = ''
                document_id = ''
                creation = ''
                repository = ''
                unit = ''
                if ExtrinsicObject.tag == '{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}ExtrinsicObject':
                    for slot in ExtrinsicObject:
                        if slot.tag == '{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Name':
                            for value in slot:
                                if value.attrib['value']:
                                    doc_name = value.attrib['value']
                        if slot.tag == '{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}ExternalIdentifier':
                            if slot.attrib['value']:
                                document_id = slot.attrib['value']
                                break
                        if slot.tag == '{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Slot' \
                                and slot.attrib['name'] == 'creationTime':
                            for ValueList in slot:
                                for value in ValueList:
                                    creation = value
                        if slot.tag == '{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Slot' \
                                and slot.attrib['name'] == 'repositoryUniqueId':
                            for ValueList in slot:
                                for value in ValueList:
                                    repository = value.text
                        if slot.tag == '{urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0}Slot'\
                                and slot.attrib['name'] == 'unit':
                            for ValueList in slot:
                                for value in ValueList:
                                    unit = value.text
                    try:
                        if document_id.startswith(translation.get_language()[:2]):
                            documents[unit] = documents.get(unit, [])
                            prepare_document_set(ExtrinsicObject, creation, doc_name, document_id, documents,
                                                 repository, unit)
                        elif not document_id.startswith(('en', 'fr', 'nl')):
                            unit = 'External'
                            documents[unit] = documents.get(unit, [])
                            prepare_document_set(ExtrinsicObject, creation, doc_name, document_id, documents,
                                                 repository, unit)
                    except AttributeError:
                        continue
    return documents


def prepare_document_set(extrinsic_object, creation, doc_name, document_id, documents, repository, unit):
    documents[unit].append({
        'repository': repository,
        'document': extrinsic_object.attrib['id'],
        'name': doc_name,
        'document_id': document_id,
        'creation': creation.text,
        'language': translation.get_language()
    })


def parse_inner_cda(data):
    result = {}
    start = data.find('<ClinicalDocument')
    end = data.find('</ClinicalDocument>', start)
    cda = data[start: end]
    try:
        root = Tree.fromstring(cda + '</ClinicalDocument>')
        for target in root:
            if target.tag == '{urn:hl7-org:v3}recordTarget':
                for role in target:
                    if role.tag == '{urn:hl7-org:v3}patientRole':
                        for patient in role:
                            if patient.tag == '{urn:hl7-org:v3}patient':
                                for patient_data in patient:
                                    try:
                                        result[patient_data.tag.replace('{urn:hl7-org:v3}', '')] = {
                                            'label': patient_data.items()[0][1],
                                            'value': patient_data.text
                                        }
                                    except IndexError:
                                        pass
                    if role.tag == '{urn:hl7-org:v3}report_comment':
                        try:
                            result[role.tag.replace('{urn:hl7-org:v3}', '')] = {
                                'label': role.items()[0][1],
                                'value': role.text
                            }
                        except IndexError:
                            pass
                    if role.tag == '{urn:hl7-org:v3}medicalReport':
                        result['medical'] = {}
                        for report in role:
                            try:
                                result['medical'][report.tag.replace('{urn:hl7-org:v3}', '')] = {
                                        'label': report.items()[0][1],
                                        'values': [{"label": value.text.split(" - ")[0], "value": value.text.split(" - ", 1)[1]} for value in report]
                                    }
                            except IndexError:
                                pass
                    if role.tag == '{urn:hl7-org:v3}drugsReport':
                        result['drugs'] = {}
                        for report in role:
                            try:
                                result['drugs'][report.tag.replace('{urn:hl7-org:v3}', '')] = {
                                        'label': report.items()[0][1],
                                        'values': [{"label": value.text.split(" - ")[0], "value": value.text.split(" - ", 1)[1]} for value in report]
                                }
                            except IndexError:
                                pass

                    if role.tag == '{urn:hl7-org:v3}evaluationReport':
                        result['evaluation'] = {}
                        for report in role:
                            try:
                                result['evaluation'][report.tag.replace('{urn:hl7-org:v3}', '')] = {
                                        'label': report.items()[0][1],
                                        'values': [{"label": value.text.split(" - ")[0], "value": value.text.split(" - ", 1)[1]} for value in report]
                                    }
                            except IndexError:
                                pass

                    if role.tag == '{urn:hl7-org:v3}socialReport':
                        result['social'] = {}
                        for report in role:
                            try:
                                result['social'][report.tag.replace('{urn:hl7-org:v3}', '')] = {
                                    'label': report.items()[0][1],
                                    'values': [{"label": value.items()[0][1], "value": value.text} for value in report]
                                }
                            except IndexError:
                                pass
    except Tree.ParseError:
        pass
    return result


def parse_cda(data):
    result = {}
    start = data.find('<ClinicalDocument')
    end = data.find('</ClinicalDocument>', start)
    cda = data[start: end]
    try:
        root = Tree.fromstring(cda + '</ClinicalDocument>')
        for target in root:
            if target.tag == '{urn:hl7-org:v3}component':
                for nonXML in target:
                    if nonXML.tag == '{urn:hl7-org:v3}nonXMLBody':
                        for text in nonXML:
                            if text.tag == '{urn:hl7-org:v3}text':
                                result['text'] = {
                                    'label': 'Comment',
                                    'value': text.text
                                }
            if target.tag == '{urn:hl7-org:v3}recordTarget':
                for role in target:
                    if role.tag == '{urn:hl7-org:v3}patientRole':
                        for patient in role:
                            if patient.tag == '{urn:hl7-org:v3}addr':
                                for addr in patient:
                                    try:
                                        if result.get('addr'):
                                            result['address']['value'] += f' {addr.text}'
                                        else:
                                            result['address'] = {
                                                'label': 'Address',
                                                'value': dict(COUNTRIES).get(addr.text, addr.text,)
                                            }
                                            result['country'] = {
                                                'label': 'Country',
                                                'value': dict(COUNTRIES).get(addr.text, addr.text)
                                            }
                                            result['nationality'] = {
                                                'label': 'Nationality',
                                                'value': dict(COUNTRIES).get(addr.text, addr.text)
                                            }
                                    except IndexError:
                                        pass
                            if patient.tag == '{urn:hl7-org:v3}patient':
                                for patient_data in patient:
                                    if patient_data.tag == '{urn:hl7-org:v3}name':
                                        for value in patient_data:
                                            try:
                                                if result.get('name'):
                                                    result['name']['value'] += f' {value.text}'
                                                else:
                                                    result['name'] = {
                                                        'label': 'Patient Name',
                                                        'value': value.text
                                                    }
                                            except IndexError:
                                                pass
                                    if patient_data.tag == '{urn:hl7-org:v3}birthTime':
                                        result['birth'] = {
                                            'label': 'Birth Date',
                                            'value': patient_data.attrib.get('value')
                                        }
                                    if patient_data.tag == '{urn:hl7-org:v3}administrativeGenderCode':
                                        result['gender'] = {
                                            'label': 'Gender',
                                            'value': dict(SEX).get(
                                                patient_data.attrib.get('code'), patient_data.attrib.get('code')
                                            )
                                        }
    except Tree.ParseError:
        pass
    return result
