from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13d
import os

small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
icon_font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.realpath(__file__)), "meteocons.ttf"), 48)

# Map the OpenWeatherMap icon code to the appropriate font character
# See http://www.alessioatzeni.com/meteocons/ for icons
ICON_MAP = {
    "01d": "B",
    "01n": "C",
    "02d": "H",
    "02n": "I",
    "03d": "N",
    "03n": "N",
    "04d": "Y",
    "04n": "Y",
    "09d": "Q",
    "09n": "Q",
    "10d": "R",
    "10n": "R",
    "11d": "Z",
    "11n": "Z",
    "13d": "W",
    "13n": "W",
    "50d": "J",
    "50n": "K",
}

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Weather_Graphics:
    def __init__(self, *, am_pm=True, celsius=True):
        self.am_pm = am_pm
        self.celsius = celsius

        self.small_font = small_font
        self.medium_font = medium_font
        self.large_font = large_font

        self._weather_icon = None
        self._city_name = None
        self._main_text = None
        self._temperature = None
        self._description = None
        self._time_text = None

    def display_weather(self, weather):
        weather = json.loads(weather.decode("utf-8"))

        # set the icon/background
        self._weather_icon = ICON_MAP[weather["weather"][0]["icon"]]

        city_name = weather["name"] + ", " + weather["sys"]["country"]
        print(city_name)
        self._city_name = city_name

        main = weather["weather"][0]["main"]
        print(main)
        self._main_text = main

        temperature = weather["main"]["temp"] - 273.15  # its...in kelvin
        print(temperature)
        if self.celsius:
            self._temperature = "%d °C" % temperature
        else:
            self._temperature = "%d °F" % ((temperature * 9 / 5) + 32)

        description = weather["weather"][0]["description"]
        description = description[0].upper() + description[1:]
        print(description)
        self._description = description
        # "thunderstorm with heavy drizzle"

        self.update_time()

    def update_time(self):
        now = datetime.now()
        self._time_text = now.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
        self.update_display()
    
    def update_display(self):
        try:
            epd = epd2in13d.EPD()
            epd.init()
            #epd.Clear(0xFF)

            image = Image.new('1', (epd.height, epd.width), 255)
            draw = ImageDraw.Draw(image)

            # Draw the Icon
            (font_width, font_height) = icon_font.getsize(self._weather_icon)
            draw.text(
                (
                    epd.height // 2 - font_width // 2 + 72,
                    epd.width // 2 - font_height // 2 - 24,
                ),
                self._weather_icon,
                font=icon_font,
                fill=0,
            )

            # Draw the city
            draw.text(
                (5, 5), self._city_name, font=self.medium_font, fill=0,
            )

            # Draw the time
            (font_width, font_height) = medium_font.getsize(self._time_text)
            draw.text(
                (5, font_height * 2 - 5),
                self._time_text,
                font=self.medium_font,
                fill=0,
            )

            # Draw the main text
            (font_width, font_height) = large_font.getsize(self._main_text)
            draw.text(
                (5, epd.width - font_height * 2),
                self._main_text,
                font=self.large_font,
                fill=0,
            )

            # Draw the description
            (font_width, font_height) = small_font.getsize(self._description)
            draw.text(
                (5, epd.width - font_height - 5),
                self._description,
                font=self.small_font,
                fill=0,
            )

            # Draw the temperature
            (font_width, font_height) = large_font.getsize(self._temperature)
            draw.text(
                (
                    epd.height - font_width - 5,
                    epd.width - font_height * 2,
                ),
                self._temperature,
                font=self.large_font,
                fill=0,
            )
            
            #rotated = image.rotate(180.0, expand=1)
            epd.DisplayPartial(epd.getbuffer(image))
            
            epd.sleep()

            #epd.Dev_exit()
            
        except IOError as e:
            print(e)
            
        except KeyboardInterrupt:    
            epd2in13d.epdconfig.module_exit()
            exit()
