import os
import config
import json
import requests # pip install requests
import datetime
import pytz
from tzlocal import get_localzone
import time
import playsound
import speech_recognition as sr
from gtts import gTTS

API_KEY = os.environ.get('API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def decimal_degrees_to_dms(degrees):
    degrees = abs(degrees)
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return d, m, s

def dms_format(latitude, longitude):
    lat_deg, lat_min, lat_sec = decimal_degrees_to_dms(latitude)
    long_deg, long_min, long_sec = decimal_degrees_to_dms(longitude)

    lat_direction = 'North' if latitude >= 0 else 'South'
    long_direction = 'East' if longitude >= 0 else 'West'

    lat_str = f"{lat_deg}°{lat_direction} with {lat_min} minutes and {lat_sec:.1f} seconds"
    long_str = f"{long_deg}°{long_direction} with {long_min} minutes and {long_sec:.1f} seconds"

    return lat_str, long_str

def offset_seconds_to_gmt(offset_seconds):
    offset_hours = offset_seconds // 3600

    if offset_hours >= 0:
        gmt_format = f"GMT +{offset_hours}"
    else:
        gmt_format = f"GMT {offset_hours}"

    return gmt_format

def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    # return round(celsius, 2)
    return round(celsius)

def get_current_time():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H-%M-%S")
    return formatted_datetime

def get_time_of_city(timezone_offset_seconds):
    offset_minutes = timezone_offset_seconds // 60
    utc_time = datetime.datetime.utcnow()
    city_timezone = pytz.FixedOffset(offset_minutes)
    city_time = utc_time.replace(tzinfo=pytz.utc).astimezone(city_timezone)
    city_date = city_time.date()
    city_current_time = city_time.strftime('%H:%M')

    return city_date, city_current_time

def get_current_city():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        city = data.get('city', 'Unknown')
        return city
    except requests.RequestException:
        return 'Unknown'

def speak(text, city):
    tts = gTTS(text=text, lang="en")
    folder_name = "speech"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = os.path.join(folder_name, f"{city}_{get_current_time()}.mp3")
    tts.save(filename)
    playsound.playsound(filename)

current_city = get_current_city()
city = input("Enter a city name: ")
request_url = f"{BASE_URL}?appid={API_KEY}&q={city}"
response = requests.get(request_url)

if response.status_code == 200:
    data = response.json()
    formatted_data = json.dumps(data, indent=5)
    # print(data)
    # print(formatted_data)

    name = data["name"]
    coord = data["coord"]

    temp_dict = {
        'temp': data["main"]["temp"],
        'temp_min': data["main"]["temp_min"],
        'temp_max': data["main"]["temp_max"],
        'feels_like': data["main"]["feels_like"]
    }

    for key, value in temp_dict.items():
        temp_dict[key] = kelvin_to_celsius(value)

    timezone = data["timezone"]
    weather = data["weather"][0]
    weather_status = weather['main']
    weather_desc = weather['description']

    lat_formatted, long_formatted = dms_format(coord["lat"], coord["lon"])
    gmt_format = offset_seconds_to_gmt(timezone)

    city_date, city_current_time = get_time_of_city(timezone)

    local_timezone = get_localzone()
    local_current_time = datetime.datetime.now(local_timezone).strftime('%Y-%m-%d %H:%M')

    weather_status_dict = {
        'Drizzle': "drizzling",
        'Smoke': "feeling smoky",
        'Ash': "full of ashes",
        'Squall': "having a squall",
        'Tornado': "having a tornado",
        'Dust': "feeling dusty",
        'Fog': "foggy",
        'Sand': "having sands on the atmosphere",
        'Mist': "having a mist",
        'Haze': "having a haze",
        'Clear': "sunny",
        'Clouds' : "cloudy",
        'Rain' : "raining",
        'Thunderstorm': "stormy",
        'Snow' : "snowing"
    }

    same_city_indicator = ""

    if current_city == name:
        same_city_indicator = "Oh well, you are looking for the weather report of your own city, don't you?"

    same_timezone_indicator = f"{local_current_time}!"
    
    if f"{city_date} {city_current_time}" == local_current_time:
        same_timezone_indicator = f"- woah, looks like it is also the exact same current time of {local_current_time}! {same_city_indicator}"
    
    opening_line = f"Welcome to the Weather Adventure! Today we will take a look at the beautiful city of {name}! As we set foot in {name}, the date is {city_date}, and the clock strikes {city_current_time} at the local time. Meanwhile, back in your city, {get_current_city()}, the current time is {same_timezone_indicator}"

    coord_line = ""

    if current_city == name:
        coord_line = f"Perhaps you might wandering, 'where is my amazing {name}'s coordinate? Where am I in this globe?' Don't worry, I'm here to tell you that your {name}'s DMS latitude longitude coordinates are {lat_formatted} and {long_formatted}."
    else:
        coord_line = f"If you are wandering, 'where is {name}?' Fear not, I'm here to tell you that {name}'s DMS latitude longitude coordinates are {lat_formatted} and {long_formatted}."

    timezone_line = f"Well how about its timezone? Indeed, the official time zone in {name} defined by an UTC offset of {gmt_format}."

    temp_line = f"Enough with the introduction, let's start our report today with {name}'s temperature! I'm here to tell you that the temperature in {name} for today is {temp_dict['temp']}° celcius! It is predicted to peak {temp_dict['temp_max']}° celcius, and reach the lowest at {temp_dict['temp_min']}° celcius. If you are at {name} at this moment, you might feel the current temperature is like {temp_dict['feels_like']}° celcius."
    
    weather_line = f"For the weather itself, it seems like {name} is {weather_status_dict[weather_status]}! I would describe the current situation as '{weather_desc}'!"

    closing_line = f"Well, that's a wrap for our report today! Thank you for tuning in and staying updated on the weather in {name}. We hope you have a wonderful day ahead, and remember to stay prepared for any changes in the weather. See you next time!"

    full_script = f"{opening_line} {timezone_line} {coord_line}\n{temp_line} {weather_line}\n{closing_line}"

    print(full_script)
    speak(full_script, name)

    """
    print(f"{opening_line} {timezone_line} {coord_line}")
    print(f"{temp_line} {weather_line}")
    print(f"{closing_line}")
    """

else:
    print("An error occurred!")

