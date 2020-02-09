from datetime import datetime


def time_convert(time):
    """Function to convert from hl7 date format to the one used in DB."""
    try:
        time_data = str(time)
        if time_data:
            try:
                time_data = datetime.strptime(time_data, '%Y%m%d')
            except Exception:
                time_data = datetime.strptime(time_data, '%Y%m%d%H%M%S')
            time_data = time_data.strftime('%Y-%m-%d')
        return time_data
    except Exception:
        return False


def get_patient_nr(segment):
    """Returns patients national_register number."""
    try:
        national_register = str(segment[19])
    except IndexError:
        nr_list = segment[2:5]
        national_register = [nr for nr in nr_list if str(nr) is not ""].pop()[0]
        national_register = str(national_register).split("^")[0]
    return national_register


def get_patient_bed_and_unit(segment):
    if not isinstance(segment, list):
        segment = segment.split(" ")

    if len(segment) < 1:
        return None, None

    new_unit = segment.pop(0) if segment[0] else None
    segment = [seg for seg in segment if seg]
    new_bed = "-".join(segment)

    return new_unit, new_bed


def get_segment_part(segment, index1, index2=None, separator="^"):
    """Returns requiered segment part, if needed - gets part of the segment field."""
    try:
        res = str(segment[index1])
    except IndexError:
        return None
    if index2:
        try:
            res = res.split(separator)[index2]
        except IndexError:
            pass
    return res.replace("^", " ")
