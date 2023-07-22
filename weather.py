import os
import config
import json
import requests # pip install requests

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

    lat_direction = 'N' if latitude >= 0 else 'S'
    long_direction = 'E' if longitude >= 0 else 'W'

    lat_str = f"{lat_deg}° {lat_min}' {lat_sec:.4f}'' {lat_direction}"
    long_str = f"{long_deg}° {long_min}' {long_sec:.4f}'' {long_direction}"

    return lat_str, long_str

def offset_seconds_to_gmt(offset_seconds):
    offset_hours = offset_seconds // 3600

    if offset_hours >= 0:
        gmt_format = f"GMT +{offset_hours}"
    else:
        gmt_format = f"GMT -{offset_hours}"

    return gmt_format

def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    # return round(celsius, 2)
    return round(celsius)

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
    country = data["sys"]["country"]

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

    opening_line = f"This is the weather report! Today we will take a look at the beautiful {name} of {country}!"
    coord_line = f"If you are wandering: 'where is that place?' Fear not, I'm here to tell you that {name}'s DMS latitude longitude coordinates are {lat_formatted} and {long_formatted}."
    timezone_line = f"Well how about its timezone? Indeed, the official time zone in {name} defined by an UTC offset of {gmt_format}."
    temp_line = f"Enough with the introduction, let's start our report today with {name}'s temperature! I'm here to tell you that the temperature in {name} for today is {temp_dict['temp']}°c, which it is predicted to peak {temp_dict['temp_max']}°c, and reach the lowest at {temp_dict['temp_min']}°c. If you are at {name} at this moment, you might feel the current temperature is like {temp_dict['feels_like']}°c."
    weather_line = f"For the weather itself, it seems like {name} is {weather_status_dict[weather_status]}! I would describe the current situation as '{weather_desc}'!"
    closing_line = f"Well, that's a wrap for our report today! Thank you for listening, and have a nice day!"


    print(f"{opening_line} {timezone_line} {coord_line}")
    print(f"{temp_line} {weather_line}")
    print(f"{closing_line}")

else:
    print("An error occurred!")