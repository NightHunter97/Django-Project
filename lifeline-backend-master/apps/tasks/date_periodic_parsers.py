import copy
import datetime

from dateutil.relativedelta import relativedelta
from apps.patients.services import get_id_by_file_id


def parse_periodic_data(data, file=None, user=None):
    data.update({
        'file': file or get_id_by_file_id(data.get('file')),
        'creator': user.pk
    })
    periodic = data.get('periodic')

    end_date = data.get('end_date')
    repeats = int(data.get('repeats', 0))
    times = sorted(data.get('times', [data.get('time')]))

    interval = int(data.get('interval', 1))
    delta = 0
    data_set = []

    try:
        start = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        if end_date:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            delta = end_date - start
    except (ValueError, TypeError):
        return data

    week_days = data.get('week_days', [start.weekday()])

    for time in times:
        data.update({'time': time})
        if periodic == 'DAY':
            data_set.extend(daily_data(start, delta, data, end_date, repeats, interval))
        elif periodic == 'WEEK':
            data_set.extend(weekly_data(start, delta, data, end_date, repeats, week_days, interval))
        elif periodic == 'MONTH':
            data_set.extend(monthly_yearly_data(start, data, end_date, repeats, {'months': 1}, interval))
        elif periodic == 'YEAR':
            data_set.extend(monthly_yearly_data(start, data, end_date, repeats, {'years': 1}, interval))
        else:
            data_set.append(copy.copy(data))
    return data_set


def daily_data(start, delta, data, end, repeats, interval=1):
    if end:
        data = [copy.copy({**data, **dict(date=start.date() + datetime.timedelta(day))}) for day in
                range(0, delta.days + 1, interval)]
        if repeats:
            data = data[:repeats]
        return data

    if repeats:
        repeat = 0
        res = []
        date = start.date()
        while repeat < repeats:
            res.append(copy.copy({**data, **dict(date=date)}))
            date += datetime.timedelta(interval)
            repeat += 1
        return res
    return []


def weekly_data(start, delta, data, end, repeats, week_days, interval=1):
    week_count = 0
    task_repeats = 0
    result = []
    if end:
        date = start.date()
        for index, _ in enumerate(range(delta.days + 1)):
            if date.weekday() == 0 and index:
                week_count += 1
            if week_count % interval == 0:
                if date.weekday() in week_days:
                    task_repeats += 1
                    if repeats and task_repeats > int(repeats):
                        break

                    result.append(copy.copy({**data, **dict(date=date)}))
            date += datetime.timedelta(1)
    elif repeats:
        repeat = 0
        start = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        date = start.date()
        while repeat < repeats:
            if date.weekday() == 0:
                week_count += 1
            if week_count % interval == 0:
                if date.weekday() in week_days:
                    task_repeats += 1
                    if repeats and task_repeats > repeats:
                        break
                    result.append(copy.copy({**data, **dict(date=date)}))
                    repeat += 1
            date += datetime.timedelta(1)
    return result


def monthly_yearly_data(start, data, end, repeats, type, interval=1):
    result = []
    month_count = 0
    task_repeats = 0
    if end:
        task_repetition = 0
        date = start.date()
        while date < end.date():
            if month_count % interval == 0:
                if date.day == start.date().day:
                    task_repetition += 1
                    if repeats and task_repetition > int(repeats):
                        break
                    result.append(copy.copy({**data, **dict(date=date)}))
            month_count += 1
            date += relativedelta(**type)
    elif repeats:
        repeat = 0
        result = []
        date = start.date()
        while repeat < int(repeats):
            if month_count % interval == 0:
                task_repeats += 1
                if task_repeats > int(repeats):
                    break
                result.append(copy.copy({**data, **dict(date=date)}))
                repeat += 1
            month_count += 1
            date += relativedelta(**type)
    return result
