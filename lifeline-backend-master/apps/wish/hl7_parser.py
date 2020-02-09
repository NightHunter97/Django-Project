from datetime import datetime

import hl7

from apps.wish.hl7_fields import PATIENT_KEYS, VISIT_KEYS, INSURANCE_2_KEYS, INSURANCE_1_KEYS
from apps.wish.hl7_tools import get_patient_nr, get_segment_part, time_convert, get_patient_bed_and_unit


def full_update(res, message, action, national_register):
    """Admit, register a patient
       Update patient information or person information
    """
    res.update(get_prime_segments(message))
    res["patient_info"].update({"national_register": national_register})

    bed = res["visit_info"].get("bed")
    if bed:
        new_unit, new_bed = get_patient_bed_and_unit(bed.split(" "))
        res["visit_info"].update({
            "bed": new_bed
        })
        if new_unit:
            res["visit_info"].update({
                "unit": new_unit
            })

    if action in ("A01", "A04"):
        try:
            created = get_segment_part(message.segment('EVN'), 6, 0)
            if created:
                res['patient_info'].update({'created': created})
        except (KeyError, IndexError):
            pass
    return res


def transfer(res, message, action, national_register):
    """Transfer a patient"""
    new_unit, new_bed = get_patient_bed_and_unit(get_segment_part(message.segment('PV1'), 3))
    res.update({
        "visit_info": {
            "bed": new_bed,
            "unit": new_unit
        }
    })
    return res


def discharge(res, message, action, national_register):
    """discharge a patient
            Cancel a patient admission
            """
    try:
        closed_since = time_convert(get_segment_part(message.segment('EVN'), 6, 0))
    except (KeyError, IndexError):
        closed_since = datetime.now().date()
    res.update(
        {
            "visit_info": {"closed_since": closed_since}
        })
    return res


def out_in_patient(res, message, action, national_register):
    """Change an outpatient to an inpatient"""
    new_unit, new_bed = get_patient_bed_and_unit(get_segment_part(message.segment('PV1'), 3))
    res.update({
        "visit_info": {
            "bed": new_bed,
            "unit": new_unit,
            "status": get_segment_part(message.segment('PV1'), 2).replace("^", "")
        }
    })
    return res


def temp_movement(res, message, action, national_register):
    """Patient temporary movement – tracking"""
    new_unit, new_bed = get_patient_bed_and_unit(get_segment_part(message.segment('PV1'), 3))
    temporary_location = get_segment_part(message.segment('PV1'), 11)
    res.update({
        "visit_info": {
            "bed": new_bed,
            "unit": new_unit,
            "temporary_location": temporary_location
        }
    })
    return res


def cancel_discharge(res, message, action, national_register):
    """Cancel discharge of a patient"""
    res.update(
        {
            "visit_info": {
                "action": action,
                "closed_since": None
            }
        })
    return res


def temp_release_start(res, message, action, national_register):
    """Patient goes on a “temporary release”"""
    start_date = get_segment_part(message.segment('EVN'), 6, 0)
    res.update(
        {
            "visit_info": {"temporary_released_start": start_date}
        })

    return res


def temp_release_end(res, message, action, national_register):
    """Patient comes back from “temporary release”"""
    try:
        end_date = get_segment_part(message.segment('EVN'), 6, 0)
        if not end_date:
            end_date = get_segment_part(message.segment('PV2'), 47, 0)
    except (KeyError, IndexError):
        return None
    res.update(
        {
            "visit_info": {"temporary_released_end": end_date}
        })
    return res


ACTION_MAPPING = {
    'A01': full_update,
    "A04": full_update,
    "A08": full_update,
    "A28": full_update,
    "A31": full_update,
    "A02": transfer,
    "A12": transfer,
    "A03": discharge,
    "A11": discharge,
    "A06": out_in_patient,
    "A07": out_in_patient,
    "A09": temp_movement,
    "A10": temp_movement,
    "A32": temp_movement,
    "A33": temp_movement,
    "A13": cancel_discharge,
    "A21": temp_release_start,
    "A22": temp_release_end
}


def dict_by_action(message: hl7.containers.Message):
    """Temp version of suppoused reactions to actions in message.
    :param message: message string, parsed with hl7 lib.
    """
    action = get_segment_part(message.segment('MSH'), 9, 1)
    national_register = get_patient_nr(message.segment('PID'))
    res = {"national_register": national_register}

    try:
        func = ACTION_MAPPING[action]
        return func(res, message, action, national_register)
    except KeyError:
        pass
    return None


def get_prime_segments(message: hl7.containers.Message):
    """Fills up dicts with data from message.
    :param message: message string, parsed with hl7 lib.
    """
    try:
        message_dict = {
            "patient_info": get_segment_info(message.segment('PID'), PATIENT_KEYS),
            "visit_info": get_segment_info(message.segment('PV1'), VISIT_KEYS)
        }
        post_code = get_segment_part(message.segment('PID'), 11, 4)
        message_dict["patient_info"].update(
            {
                "post_code": post_code
            }
        )
    except (KeyError, IndexError):
        return None

    try:
        message_dict.update({"insurance_info": get_segment_info(message.segment('IN1'), INSURANCE_1_KEYS)})
        message_dict["insurance_info"].update(get_segment_info(message.segment('IN2'), INSURANCE_2_KEYS))
    except KeyError:
        pass
    return message_dict


def get_segment_info(segment, keys_list):
    """Creates a dict out of segment values and provided keys.
    :param segment: segment of message
    :param keys_list: list of keys to dict
    """

    info = {}
    for key in keys_list:
        try:
            value = get_segment_part(segment, keys_list.index(key) + 1)
            if not value:
                continue
            info.update({key: value})
        except IndexError:
            break
    return info


def parse_hl7_file(file_data):
    """Opens file and parses it with hl7 lib.
    :param file_data: file lines
    """
    if not file_data:
        return []

    message = ""
    for line in file_data:
        message += line.decode("utf-8")

    message_list = []
    message = "\r".join(message.splitlines())
    message = hl7.split_file(message)
    for mess in message:
        parsed_message = hl7.parse(mess)
        res_dict = dict_by_action(parsed_message)
        if res_dict:
            message_list.append(res_dict)

    return message_list
