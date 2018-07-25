#!/usr/bin/env python


import ephem
import datetime
from dateutil.tz import UTC
 
Sun = ephem.Sun()


def get_next_shabbat(dt):
    cur = dt.weekday()
    sat = 5
    if cur == 6:
        delta = 6
    elif cur == sat:
        delta = 7
    else:
        delta = sat - cur
    return dt + datetime.timedelta(days=delta)

def get_sunset_sunrise(date, lat, lng):
    moshe = ephem.Observer()
    moshe.date = str(date)
    moshe.lat = lat
    moshe.lon = lng
    moshe.elevation = 0
    return moshe.previous_setting(Sun), moshe.next_setting(Sun)
 

def candle_lighting_time(sunset):
    return sunset - datetime.timedelta(minutes=18)


def havdala_time(sunset):
    return sunset + datetime.timedelta(minutes=50)


def dd_to_dms(dd):
   is_positive = dd >= 0
   dd = abs(dd)
   minutes,seconds = divmod(dd*3600,60)
   degrees,minutes = divmod(minutes,60)
   degrees = degrees if is_positive else -degrees
   return (degrees,minutes,seconds)

    

if __name__ == '__main__':
    import sys
    yyyy, mm, dd =  (int(a) for a in sys.argv[1:4])
    lat, lng = (a for a in sys.argv[4:6])
    if ':' not in lat:
        lat = ':'.join(str(a) for a in dd_to_dms(float(lat)))
        lng = ':'.join(str(a) for a in dd_to_dms(float(lng)))

    dt = datetime.datetime(yyyy, mm, dd, 12)
    next_shabbat = get_next_shabbat(dt)
    entry, out = get_sunset_sunrise(next_shabbat, lat, lng)
    print(ephem.localtime(out))
    print("Light Shabbat lights at", candle_lighting_time(ephem.localtime(entry)))
    print("Perform Havdalah at", havdala_time(ephem.localtime(out)))
