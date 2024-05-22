from datetime import datetime
# python time zone
import pytz

def utc_now():
    return datetime.now().replace(tzinfo=pytz.utc)