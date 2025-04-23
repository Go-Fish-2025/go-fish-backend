from datetime import datetime, date

import requests
from flask import Blueprint, jsonify, request

weather_bp = Blueprint('weather', __name__)

def get_coordinates(location):
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&format=json"
    try:
        response = requests.get(geocoding_url)
        response.raise_for_status()
        data = response.json()
        if "results" not in data or not data["results"]:
            return None, f"No results found for location: {location}"
        result = data["results"][0]
        return {
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "timezone": result["timezone"]
        }, None
    except requests.RequestException as e:
        return None, f"Geocoding error: {str(e)}"

def get_weather_data(latitude, longitude, timezone):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,weather_code&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_direction_10m_dominant,sunrise,sunset,precipitation_sum,weather_code&timezone={timezone}&forecast_days=14"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as e:
        return None, f"Weather API error: {str(e)}"

def interpret_storm_alert(weather_code, precip_sum):
    severe_codes = [95, 96, 99]
    moderate_codes = [63, 64, 65]
    minor_codes = [61, 62]

    if weather_code in severe_codes:
        return "Severe Storm Alert: Thunderstorm possible!"
    elif weather_code in moderate_codes or precip_sum > 15:
        return "Moderate Storm Warning: Heavy rain expected."
    elif weather_code in minor_codes or precip_sum > 10:
        return "Minor Storm Risk: Light rain possible."
    else:
        return "No storm risk."

@weather_bp.route('')
def weather():
    location = request.args.get('location')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    timezone = request.args.get('timezone')

    if not timezone:
        timezone = "America%2FNew_York"

    if not location and (not latitude or not longitude):
        return jsonify({"error": "Missing details"}), 400

    if location:
        coords, error = get_coordinates(location)
        if error:
            return jsonify({"error": error}), 400
    else:
        coords = {
            "latitude": latitude,
            "longitude":longitude,
            "timezone": timezone
        }

    data, error = get_weather_data(coords["latitude"], coords["longitude"], coords["timezone"])
    if error:
        return jsonify({"error": error}), 500

    current = {
        "temperature": data["hourly"]["temperature_2m"][0],
        "wind_speed": data["hourly"]["wind_speed_10m"][0],
        "wind_direction": data["hourly"]["wind_direction_10m"][0],
        "precipitation": data["hourly"]["precipitation"][0],
        "weather_code": data["hourly"]["weather_code"][0],
        "time": datetime.fromisoformat(data["hourly"]["time"][0]).strftime("%Y-%m-%d %H:%M")
    }

    today = {
        "sunrise": datetime.fromisoformat(data["daily"]["sunrise"][0]).strftime("%H:%M"),
        "sunset": datetime.fromisoformat(data["daily"]["sunset"][0]).strftime("%H:%M"),
        "precipitation_sum": data["daily"]["precipitation_sum"][0]
    }

    storm_alert = interpret_storm_alert(current["weather_code"], current["precipitation"])

    today_date = date.today().isoformat()
    hourly_forecast = []
    for i, time_str in enumerate(data["hourly"]["time"]):
        time_dt = datetime.fromisoformat(time_str)
        if time_dt.date().isoformat() == today_date:
            hour = {
                "time": time_dt.strftime("%H:%M"),
                "temperature": data["hourly"]["temperature_2m"][i],
                "wind_speed": data["hourly"]["wind_speed_10m"][i],
                "wind_direction": data["hourly"]["wind_direction_10m"][i],
                "precipitation": data["hourly"]["precipitation"][i],
                "weather_code": data["hourly"]["weather_code"][i],
                "storm_alert": interpret_storm_alert(data["hourly"]["weather_code"][i], data["hourly"]["precipitation"][i])
            }
            hourly_forecast.append(hour)

    forecast = []
    for i in range(14):
        day = {
            "date": data["daily"]["time"][i],
            "temperature_max": data["daily"]["temperature_2m_max"][i],
            "temperature_min": data["daily"]["temperature_2m_min"][i],
            "wind_speed_max": data["daily"]["wind_speed_10m_max"][i],
            "wind_direction_dominant": data["daily"]["wind_direction_10m_dominant"][i],
            "precipitation_sum": data["daily"]["precipitation_sum"][i],
            "weather_code": data["daily"]["weather_code"][i],
            "sunrise": datetime.fromisoformat(data["daily"]["sunrise"][i]).strftime("%H:%M"),
            "sunset": datetime.fromisoformat(data["daily"]["sunset"][i]).strftime("%H:%M"),
            "storm_alert": interpret_storm_alert(data["daily"]["weather_code"][i], data["daily"]["precipitation_sum"][i])
        }
        forecast.append(day)

    response = {
        "location": location,
        "coordinates": {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "timezone": coords["timezone"]
        },
        "current": current,
        "today": today,
        "storm_alert": storm_alert,
        "hourly_forecast": hourly_forecast,
        "forecast": forecast
    }

    return jsonify(response)