#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A simplistic HTTP-server that returns the local time as a json-structure.
#
# The program is meant to be a dropin-replacement for worldtimeapi.org
# (DateTimeJsonResponse only!). One additional field is supplied: struct_time
#
# Example from http://worldtimeapi.org/:
#
# {
#   "abbreviation": "CEST",
#   "client_ip": "94.216.80.157",
#   "datetime": "2022-10-09T07:29:09.226518+02:00",
#   "day_of_week": 0,
#   "day_of_year": 282,
#   "dst": true,
#   "dst_from": "2022-03-27T01:00:00+00:00",
#   "dst_offset": 3600,
#   "dst_until": "2022-10-30T01:00:00+00:00",
#   "raw_offset": 3600,
#   "timezone": "Europe/Berlin",
#   "unixtime": 1665293349,
#   "utc_datetime": "2022-10-09T05:29:09.226518+00:00",
#   "utc_offset": "+02:00",
#   "week_number": 40
# }
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-localtime-api
#
# ----------------------------------------------------------------------------

CONFIG_FILE = "py-localtime-api.json"

import locale, datetime, http.server, json, signal, os, sys, pytz

# for testing: use the config-file from the repo
config_file = os.path.join(
  os.path.dirname(sys.argv[0]),"..","..","..","etc",CONFIG_FILE)

if not os.path.exists(config_file):
  config_file = os.path.join("/etc",CONFIG_FILE)

with open(config_file,"r") as f:
  SETTINGS = json.load(f)

# --- handler class   --------------------------------------------------------

class LocalTimeApi(http.server.BaseHTTPRequestHandler):
  """ Request-handler class """

  def log_request(*args,**kw):
    """ prevent logging """
    pass

  def do_GET(self):
    """ process get-requests """

    tz = pytz.timezone(SETTINGS["TZ_NAME"])
    now = datetime.datetime.now(tz)
    tt = now.timetuple()
    tt_tuple = (tt.tm_year,tt.tm_mon,tt.tm_mday,tt.tm_hour,tt.tm_min,
                tt.tm_sec,tt.tm_wday,tt.tm_yday,tt.tm_isdst)
    dst_dates = [x for x in tz._utc_transition_times if x.year == now.year]
    data = {
      "abbreviation": now.tzname(),
      "client_ip": self.address_string(),
      "datetime": now.isoformat(),
      "day_of_week": now.isoweekday() % 7,    # worldtimeapi: Sunday==0
      "day_of_year": tt.tm_yday,
      "dst": now.dst().seconds > 0,
      "dst_from": dst_dates[0].isoformat(),
      "dst_offset": now.dst().seconds,
      "dst_until": dst_dates[1].isoformat(),
      "raw_offset": int(now.utcoffset().seconds),
      "timezone": tz.zone,
      "unixtime": int(now.timestamp()),
      "utc_datetime": now.astimezone(tz=datetime.timezone.utc).isoformat(),
      "utc_offset": now.isoformat()[-6:],
      "week_number": int(now.strftime("%W")),
      "struct_time": tt_tuple 
      }

    json_data = json.dumps(data,indent=2).encode(encoding='utf_8')
    self.send_response(http.HTTPStatus.OK.value)
    self.send_header("Content-Type","application/json")
    self.send_header("Content-Length",str(len(json_data)))
    self.end_headers()
    self.wfile.write(json_data)

# --- signal handler   -------------------------------------------------------

def signal_handler(_signo,_stack_frame):
  """ signal-handler for clean shutdown """
  sys.exit(0)

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # setup signal-handler
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGINT,  signal_handler)

  httpd = http.server.HTTPServer(('',SETTINGS["PORT"]),LocalTimeApi)
  print("running LocalTimeApi-Server on: 0.0.0.0:%d" % SETTINGS["PORT"])
  httpd.serve_forever()
