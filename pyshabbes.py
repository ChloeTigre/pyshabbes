#!/usr/bin/env python

import ephemerides
import datetime
import pytz

def get_first_friday(t:datetime.date=None):
    if t is None:
        t = datetime.date.today()
    while t.weekday() != 4:
        t += datetime.timedelta(1)
    return t


class City(ephemerides.ComputeRequest):
    @property
    def city_name(self):
        return self._city

    @property
    def timezone(self):
        return self._timezone
    @property
    def city_coordinates(self):
        return self._city_coordinates

    @property
    def latitude(self):
        return self._city_coordinates[0]

    @property
    def longitude(self):
        return self._city_coordinates[1]
    
    def __init__(self, city, latitude, longitude, timezone):
        self._city = city
        self._timezone = timezone
        self._city_coordinates = (ephemerides.Degree(latitude), ephemerides.Degree(longitude)) 


class NextShabbosTime(object):
    @property
    def shabbos_entry(self):
        return (self._shabbos_entry_date + datetime.timedelta(minutes=self._entry_sunset.time - 18)).astimezone(self._city.timezone)

    @property
    def shabbos_exit(self):
        return (self._shabbos_exit_date + datetime.timedelta(minutes=self._exit_sunset.time + 50)).astimezone(self._city.timezone)

    def __str__(self):
        return "For {city}, upcoming shabbat candle lighting time is {entry} and havdalah time is {exit}".format(
            city=self._city.city_name,
            entry=self.shabbos_entry.strftime('%H:%M'), 
            exit=self.shabbos_exit.strftime("%H:%M"))

    def __init__(self, city: City, start_date: datetime.date = datetime.date.today()):
        self._city = city
        shabbos_entry_date = get_first_friday(start_date)
        self._shabbos_entry_date = datetime.datetime(shabbos_entry_date.year, shabbos_entry_date.month, shabbos_entry_date.day, 0, 0, 0, 0, pytz.UTC)
        self._shabbos_exit_date = self._shabbos_entry_date + datetime.timedelta(1)
        _, self._entry_sunset = ephemerides.ComputeRequest(city.city_name, city.latitude, city.longitude, self._shabbos_entry_date).compute()
        _, self._exit_sunset = ephemerides.ComputeRequest(city.city_name, city.latitude, city.longitude, 
        self._shabbos_exit_date).compute()



print(datetime.datetime.now())
for i in range(10000):
    Paris = City("Paris", 48.866667, -2.333333, pytz.timezone('Europe/Paris'))
    NewYork = City("New-York", 40.7142700, 74.0059700, pytz.timezone('America/New_York'))
    nst = NextShabbosTime(Paris)
    nst2 = NextShabbosTime(NewYork)

    r = str(nst)
    r2 = str(nst2)
print(datetime.datetime.now())
print(r)
print(r2)