from datetime import datetime, timedelta
import pytz
CHART_PARTS = 12


def get_parsed_data(qs, from_date, to, tz):
    if not qs:
        return qs
    res = []
    try:
        day = datetime.strptime(to, "%Y-%m-%d") if to else qs[0].created
        day += timedelta(days=1)
        end = datetime(day.year, day.month, day.day, tzinfo=pytz.timezone(tz) if tz else pytz.UTC)
        day = datetime.strptime(from_date, "%Y-%m-%d") if from_date else qs[-1].created
        start = datetime(day.year, day.month, day.day, tzinfo=pytz.timezone(tz) if tz else pytz.UTC)
        delta = (end - start) / CHART_PARTS
    except (TypeError, ValueError):
        return res

    for scope in range(CHART_PARTS):
        points = [item.value for item in qs if start <= item.created <= start+delta]
        value = sum_items(points, qs[0].type)
        res.append({'created': start.replace(tzinfo=None) + delta - timedelta(seconds=1), 'value': value})
        start += delta
    return res


def sum_items(qs, type):
    qs_len = len(qs)
    if type == 'pressure':
        max_sum = 0
        min_sum = 0
        if not qs_len:
            return [0, 0]

        for item in qs:
            if '/' not in item:
                continue
            max, min = item.split('/')
            max_sum += to_float(max)
            min_sum += to_float(min)
        return [max_sum/qs_len, min_sum/qs_len]
    if not qs_len:
        return 0
    return sum(to_float(item) for item in qs)/qs_len


def to_float(value):
    try:
        return float(value)
    except ValueError:
        return 0
