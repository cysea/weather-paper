#!/usr/bin/python3

import urllib.request
import urllib.parse
import time
from weather_graphics import Weather_Graphics

ow_token = ""
ow_url = "http://api.openweathermap.org/data/2.5/weather"
location = ""

if len(ow_token) == 0:
    raise RuntimeError(
        "You need to set your token first. If you don't already have one, you can register for a free account at https://home.openweathermap.org/users/sign_up"
    )

params = {"q": location, "appid": ow_token}
data_source = ow_url + "?" + urllib.parse.urlencode(params)

gfx = Weather_Graphics(am_pm=True, celsius=True)
weather_refresh = None

while True:
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        response = urllib.request.urlopen(data_source)
        if response.getcode() == 200:
            value = response.read()
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
        else:
            print("Unable to retrieve data at {}".format(url))

    gfx.update_time()
    time.sleep(600)
