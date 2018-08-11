#!/usr/bin/env python
"""ephemerides

This library aims to compute with a reasonable accuracy sunset and sunrise
times in pure python.

Based on advice and examples by Nathanaëlle Mouniée 
"""

import datetime
import math
import pytz

class AU(object):
    @property
    def distance(self):
        return self._distance

    def __init__(self, distance):
        self._distance = distance


class Angle(object):
    @property
    def angle(self):
        return self._angle

    def __init__(self, angle):
        self._angle = float(angle)


class Degree(Angle):
    def __str__(self):
        return "%3.2f deg " % (self.angle,)

    def as_degree(self):
        return self

    def as_radian(self):
        return Radian(math.radians(self.angle))

    def sin(self) -> float:
        return math.sin(math.pi * self.angle / 180.0)

    def sin2(self) -> float:
        return math.sin(math.pi * self.angle / 90.0)

    def sin3(self) -> float:
        return math.sin(math.pi * self.angle / 60.0)

    def sin4(self) -> float:
        return math.sin(math.pi * self.angle / 45.0)
    
    def cos(self) -> float:
        return math.cos(math.pi * self.angle / 180.0)

    def cos2(self) -> float:
        return math.cos(math.pi * self.angle / 90.0)

    def tan(self) -> float:
        return math.tan(math.pi * self.angle / 180.0)

    def tan05(self) -> float:
        return math.tan(math.pi * self.angle / 360.0)

    def ratio(self) -> float:
        return self.angle / 360

    def add(self, other: Angle) -> Angle:
        return Degree(self.angle + other.as_degree().angle)

    def sub(self, other: Angle) -> Angle:
        return Degree(self.angle - other.as_degree().angle)

    def neg(self) -> Angle:
        return Degree(-self.angle)
    

class Radian(Angle):
    def __str__(self):
        return "%3.2f rad " % (self.angle,)

    def as_degree(self):
        return Degree(math.degrees(self.angle))

    def as_radian(self):
        return self

    def sin(self) -> float:
        return math.sin(self.angle)

    def sin2(self) -> float:
        return math.sin(self.angle + self.angle)

    def sin3(self) -> float:
        return math.sin(self.angle + self.angle + self.angle)

    def sin4(self) -> float:
        return math.sin(self.angle + self.angle + self.angle + self.angle)
    
    def cos(self) -> float:
        return math.cos(self.angle)

    def cos2(self) -> float:
        return math.cos(self.angle + self.angle)

    def tan(self) -> float:
        return math.tan(self.angle)

    def tan05(self) -> float:
        return math.tan(self.angle / 2)

    def ratio(self) -> float:
        return self.angle / (2 * math.pi)

    def add(self, other: Angle) -> Angle:
        return Radian(self.angle + other.as_radian().angle)

    def sub(self, other: Angle) -> Angle:
        return Radian(self.angle - other.as_radian().angle)

    def neg(self) -> Angle:
        return Radian(-self.angle)


class ReverseTrigonometry(object):
    @staticmethod
    def acos(val: float) -> Angle:
        return Radian(math.acos(val))
  
    @staticmethod
    def atan2(num: float, denom: float) -> Angle:
        return Radian(math.atan2(num, denom))

    @staticmethod
    def asin(val: float) -> Angle:
        return Radian(math.asin(val))


def as_degree(n: float) -> Degree:
    return Degree(math.fmod(n, 360))


def as_radian(n: float) -> Radian:
    return Radian(math.fmod(n, 2 * math.pi))


def deg_min_sec(deg: int, min: int, sec: float) -> Degree:
    if deg < 0:
        return Degree(float(deg) - (float(min)+sec/60)/60)
    else:
        return Degree(float(deg) + (float(min)+sec/60)/60)


class Minute(object):
    @property
    def time(self):
        return self._time

    def __init__(self, tim: float):
        self._time = tim

    def __str__(self):
        sign = ""
        t = self.time
        if t < 0:
            t = -t
            sign = "-"
        hr = int(t / 60)
        mn = int(t + 0.5) % 60

        return "%s%02d:%02d" % (sign, hr, mn)

    def ratio(self) -> float:
        return self.time / 1440
    
    def add(self, other: "Minute"):
        return Minute(self.time + other.time)

    def sub(self, other: "Minute"):
        return Minute(self.time - other.time)


HALF_DAY = Minute(720)


def angle_to_minute(angle: Angle) -> Minute:
    return Minute(angle.ratio() * 1440)


class JulianTimeComputeUnit(object):
    @property
    def date(self):
        return self._date

    def __init__(self, date):
        self._date = date


class JulianDay(JulianTimeComputeUnit):
    def __str__(self):
        return "%13.6f JD" % (self.date,)
    
    def as_century(self) -> "JulianCentury":
        return JulianCentury((self.date - 2451545.0) / 36525.0)

    def add(self, other: "JulianDay") -> "JulianDay":
        return JulianDay(self.date + other.date)
    
    def correct(self, ratio_ish) -> "JulianDay":
        return JulianDay(self.date + ratio_ish.ratio())

    def time(self) -> datetime.datetime:
        frac0, days = math.modf(self.date + 0.5)
        frac, hr0 = math.modf(frac0 * 24)
        frac, mn0 = math.modf(frac * 60)
        frac, sc0 = math.modf(frac * 60)

        hr = int(hr0)
        mn = int(mn0)
        sc = int(sc0)

        a = days

        if days >= 2299161:
            alpha = math.floor((days - 1867216.25) / 36524.25)
            a = days + 1 + alpha - math.floor(alpha / 4)
        
        b = a + 1524
        c = math.floor((b - 122.1) / 365.25)
        d = math.floor(365.25 * c)
        e = math.floor((b - d) / 30.6001)

        dd = b - d - math.floor(30.6001 * e) + frac0

        mm = e - 13
        if e < 14:
            mm = e - 1
        
        yyyy = c - 4715
        if mm > 2:
            yyyy -= 1
        return datetime.datetime(int(yyyy), mm, int(dd), hr, mn, sc, 0, pytz.utc)
    

def new_day(y: int, m: int, d: int) -> JulianDay:
    if m <= 2:
        y -= 1
        m += 12
    cen = math.floor(float(y) / 100)
    b = 2 - cen + math.floor(cen / 4)
    return JulianDay(math.floor(365.25 * float(y + 4716)) + 
                     math.floor(30.6001 * float(m + 1)) + 
                     float(d) + b - 1524.5)

class JulianCentury(JulianTimeComputeUnit):
    def as_day(self) -> JulianDay:
        return JulianDay(self.date * 36525.0 + 2451545.0)

    def geometric_mean_longitude_of_sun(self) -> Degree:
        l0 = 280.46646 + self.date * (36000.76983 + 0.0003032 * self.date)
        # trick to get l0 as an accurate value in [0, 360[
        l0 = math.fmod(l0, 360)
        l0 += 360
        l0 = math.fmod(l0, 360)
        return as_degree(l0)

    def geometric_mean_anomaly_of_sun(self) -> Degree:
        return as_degree(357.52911 + self.date * (35999.05029 - 0.0001537 * self.date))
    
    def eccentricity_of_earth_orbit(self) -> Degree:
        return 0.016708634 - self.date * (0.00042037 + 0.0000001267 * self.date)

    def equation_of_center_of_sun(self) -> Degree:
        anomaly = self.geometric_mean_anomaly_of_sun()

        sinm = anomaly.sin()
        sin2m = anomaly.sin2()
        sin3m = anomaly.sin3()

        return as_degree(sinm * (1.914602 - self.date * (0.004817 + 0.000014 * self.date)) + 
                         sin2m * (0.019993 - 0.000101 * self.date) +
                         sin3m * 0.000289)


    def omega(self) -> Degree:
        return as_degree(125.04 - 1934.136 * self.date)

    def sun_radius_length(self) -> AU:
        a0 = self.geometric_mean_anomaly_of_sun()
        center = self.equation_of_center_of_sun()

        anomaly = a0.add(center)
        ecc = self.eccentricity_of_earth_orbit()

        return AU((1.000001018 * (1 - ecc * ecc)) / (1 + ecc * anomaly.cos()))

    def sun_apparent_longitude(self) -> Degree:
        l0 = self.geometric_mean_longitude_of_sun()
        center = self.equation_of_center_of_sun()
        longitude = l0.add(center)
        omega = self.omega()

        return longitude.sub(as_degree(0.00569 + 0.00478 * omega.sin()))
    
    def obliquity_correction(self) -> Degree:
        seconds = 21.448 - self.date * (46.8150 + self.date * (0.00059 - self.date * 0.001813))
        ecliptic = deg_min_sec(23, 26, seconds)
        omega = self.omega()

        return ecliptic.add(as_degree(0.00256 * omega.cos()))

    def sun_right_ascension(self) -> Angle:
        eps = self.obliquity_correction()
        lam = self.sun_apparent_longitude()

        return ReverseTrigonometry.atan2(eps.cos() * lam.sin(), lam.cos())
    
    def sun_declination(self) -> Angle:
        eps = self.obliquity_correction()
        lam = self.sun_apparent_longitude()

        return ReverseTrigonometry.asin(eps.sin() * lam.sin())

    def equation_of_time(self) -> Minute:
        eps = self.obliquity_correction()
        l0 = self.geometric_mean_longitude_of_sun()
        ecc = self.eccentricity_of_earth_orbit()
        anomaly = self.geometric_mean_anomaly_of_sun()

        tanE = eps.tan05()
        y = tanE * tanE

        sin2l0 = l0.sin2()
        sinm = anomaly.sin()
        cos2l0 = l0.cos2()
        sin4l0 = l0.sin4()
        sin2m = anomaly.sin2()

        etime = (((y * sin2l0 - 2.0 * ecc * sinm) + 
                (4.0 * ecc * y * sinm * cos2l0 - 0.5 * y * y * sin4l0) - 
                (1.25 * ecc * ecc * sin2m)))

        return angle_to_minute(as_radian(etime))

# here comes time for computation

ANGLE_AT_HORIZON = as_degree(90.833)

def calc_hour_angle_sunrise(lat: Angle, solar_declination: Angle) -> Angle:
    cosLat = lat.cos()
    cosDec = solar_declination.cos()
    tanLat = lat.tan()
    tanDec = solar_declination.tan()
    haCos = ANGLE_AT_HORIZON.cos() / (cosLat * cosDec) - tanLat * tanDec
    return ReverseTrigonometry.acos(haCos)


def calc_hour_angle_sunset(lat: Angle, solar_declination: Angle) -> Angle:
    cosLat = lat.cos()
    cosDec = solar_declination.cos()
    tanLat = lat.tan()
    tanDec = solar_declination.tan()
    haCos = ANGLE_AT_HORIZON.cos() / (cosLat * cosDec) - tanLat * tanDec
    return ReverseTrigonometry.acos(haCos).neg().as_degree()


def solar_noon(jc: JulianCentury, longitude: Angle) -> Minute:
    jd = jc.as_day()
    jcNoon = jd.correct(longitude).as_century()
    eqTime = jcNoon.equation_of_time()
    newJC = jd.correct(angle_to_minute(longitude).sub(eqTime)).as_century()
    eqTime2 = newJC.equation_of_time()
    return HALF_DAY.add(angle_to_minute(longitude)).sub(eqTime2)


def sunrise_utc(jd: JulianDay, latitude: Angle, longitude: Angle) -> Minute:
    jc = jd.as_century()
    noonMin = solar_noon(jc, longitude)

    jcNoon = jd.correct(noonMin).as_century()

    eqTime = jcNoon.equation_of_time()
    solarDec = jcNoon.sun_declination()
    hour_angle = calc_hour_angle_sunrise(latitude, solarDec).as_degree()
    delta = longitude.sub(hour_angle)
    time_utc = HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)

    newJC = jd.correct(time_utc).as_century()

    eqTime = newJC.equation_of_time()
    solarDec = newJC.sun_declination()
    hour_angle = calc_hour_angle_sunrise(latitude, solarDec).as_degree()
    delta = longitude.sub(hour_angle)
    time_utc = HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)

    newJC = jd.correct(time_utc).as_century()

    eqTime = newJC.equation_of_time()
    solarDec = newJC.sun_declination()
    hour_angle = calc_hour_angle_sunrise(latitude, solarDec).as_degree()
    delta = longitude.sub(hour_angle)
    time_utc = HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)


    return HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)


def sunset_utc(jd: JulianDay, latitude: Angle, longitude: Angle) -> Minute:
    jc = jd.as_century()
    noonMin = solar_noon(jc, longitude)


    jcNoon = jd.correct(noonMin).as_century()

    eqTime = jcNoon.equation_of_time()
    solarDec = jcNoon.sun_declination()
    hour_angle = calc_hour_angle_sunset(latitude, solarDec)
    delta = longitude.sub(hour_angle)
    time_utc = HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)

    newJC = jd.correct(time_utc).as_century()

    eqTime = newJC.equation_of_time()
    solarDec = newJC.sun_declination()
    hour_angle = calc_hour_angle_sunset(latitude, solarDec).as_degree()
    delta = longitude.sub(hour_angle)
    time_utc = HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)

    newJC = jd.correct(time_utc).as_century()

    eqTime = newJC.equation_of_time()
    solarDec = newJC.sun_declination()
    hour_angle = calc_hour_angle_sunset(latitude, solarDec).as_degree()
    delta = longitude.sub(hour_angle)
    time_utc = HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)

    return HALF_DAY.add(angle_to_minute(delta)).sub(eqTime)


class ComputeRequest(object):
    @property
    def city_name(self):
        return self._city

    @property
    def city_coordinates(self):
        return self._city_coordinates

    @property
    def latitude(self):
        return self._city_coordinates[0]

    @property
    def longitude(self):
        return self._city_coordinates[1]

    @property
    def date(self):
        return self._date

    def __init__(self, city, latitude, longitude, date):
        self._city = city
        self._date = date
        self._city_coordinates = (latitude, longitude)

    def compute(self):
        jd = new_day(self.date.year, self.date.month, self.date.day)
        rise = sunrise_utc(jd, self.latitude, self.longitude)
        sset = sunset_utc(jd, self.latitude, self.longitude)
        return rise, sset
    
    def __str__(self):
        r, s = self.compute()
        return "For {i.city_name} ({i.latitude} ; {i.longitude}) on {i.date}\n\tSunrise at {sunrise}\n\tSunset at {sunset}".format(
            i=self, sunrise=r, sunset=s
        )


def test_compute():
    paris = (deg_min_sec(48, 51, 51.475), deg_min_sec(-2, 23, 20.683))
    newyork = (deg_min_sec(40, 43, 0), deg_min_sec(74, 1, 0))
    darwin = (deg_min_sec(-12, 27, 0), deg_min_sec(-130, 50, 0))
    buenos = (deg_min_sec(-34, 36, 0), deg_min_sec(58, 22, 0))

    apr1 = datetime.datetime(2018, 4, 1)
    epoch = datetime.datetime(1970, 1, 1)

    reqs = []
    reqs.append(ComputeRequest("paris", *paris, apr1))
    reqs.append(ComputeRequest("paris", *paris, epoch))
    reqs.append(ComputeRequest("newyork", *newyork, apr1))
    reqs.append(ComputeRequest("newyork", *newyork, epoch))
    reqs.append(ComputeRequest("darwin", *darwin, apr1))
    reqs.append(ComputeRequest("darwin", *darwin, epoch))
    reqs.append(ComputeRequest("buenos", *buenos, apr1))
    reqs.append(ComputeRequest("buenos", *buenos, epoch))
    for r in reqs:
        print(r)


if __name__ == '__main__':
    test_compute()