import time
from datetime import datetime

def get_datetime_str_from_timestamp(timestamp):
  """ js timestmap to valid django DateTimeFiled string """
  valid_timestamp = timestamp / 1000
  return datetime.fromtimestamp(valid_timestamp)

def get_now_datetime():
  return datetime.utcnow()

def get_js_timestamp(time_obj_or_str):
  """ get timestamp from datetime filed obj/str """

  # @TODO
  #   when serializer is invoked directly from test
  #   environment it returns string from `DateTimeField` of model obj
  #   however in case of APIClient call we have `date` object
  #   we need to discuss how dangerous this case might be
  #

  date_time_obj = datetime.strptime(
      time_obj_or_str, "%Y-%m-%dT%H:%M%z") if type(time_obj_or_str) == str else time_obj_or_str

  return int(time.mktime(date_time_obj.timetuple()) * 1000)
