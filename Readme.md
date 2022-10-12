Localtime API Server
====================

This project implements a simplistic HTTP-server that returns
the local time as a json-structure:

    > wget -qO - http://localhost:11080/
    {
      "abbreviation": "CEST",
      "client_ip": "10.173.112.202",
      "datetime": "2022-10-11T13:36:45.560818+02:00",
      "day_of_week": 2,
      "day_of_year": 284,
      "dst": true,
      "dst_from": "2022-03-27T01:00:00",
      "dst_offset": 3600,
      "dst_until": "2022-10-30T01:00:00",
      "raw_offset": 7200,
      "timezone": "Europe/Berlin",
      "unixtime": 1665488205,
      "utc_datetime": "2022-10-11T11:36:45.560818+00:00",
      "utc_offset": "+02:00",
      "week_number": 41,
      "struct_time": [
        2022,
        10,
        11,
        13,
        36,
        45,
        1,
        284,
        1
      ]
    }

The program is meant to be a dropin-replacement for worldtimeapi.org
(DateTimeJsonResponse only!). Worldtimeapi.org is notoriously unreliable
and also implements rate-limiting.

To provide the local time to devices in your LAN, just install this
Localtime API deamon to a debian-based server. It should also run
on other platforms, but in this case you have to adapt the install-routine.

Note that the api will return the data regardless of url or any
query parameters.


Installation
------------

    git clone https://github.com/bablokb/py-localtime-api.git
    cd py-localtime-api
    sudo tools/install

The installation script creates a new technical user `localtime` and
a systemd-service `py-localtime-api.service`. The script installs
one additional package: python3-tz (aka pytz).


Configuration
-------------

Edit `/etc/py-localtime-api.json`, define the port and your location:

    {
      "PORT":      11080,
      "TZ_NAME":   "Europe/Berlin"
    }

Once configured, start the service with

    sudo systemctl start py-localtime-api.service


Limitations
-----------

The program hasn't been tested yet when dst is false.


Additions
---------

One additional field is supplied: struct_time. With this field, the
creation of a `time.struct_time`-object from within Python is possible
without parsing any of the other fields. Just convert the content of
the field to a tuple and pass it to `time.struct_time()`.
