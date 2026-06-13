import requests
import asyncio

# WMO Weather Interpretation Codes (WMO code list)
WMO_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌧️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    56: "Light freezing drizzle 🌧️",
    57: "Dense freezing drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    66: "Light freezing rain 🌧️",
    67: "Heavy freezing rain 🌧️",
    71: "Slight snow fall ❄️",
    73: "Moderate snow fall ❄️",
    75: "Heavy snow fall ❄️",
    77: "Snow grains ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌦️",
    82: "Violent rain showers 🌧️",
    85: "Slight snow showers 🌨️",
    86: "Heavy snow showers 🌨️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️"
}

def get_coordinates_sync(location):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location,
        "count": "1",
        "language": "en",
        "format": "json"
    }
    response = requests.get(url, params=params, timeout=5)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results")
        if results:
            first = results[0]
            return {
                "name": first.get("name"),
                "country": first.get("country"),
                "admin1": first.get("admin1"),
                "latitude": first.get("latitude"),
                "longitude": first.get("longitude")
            }
    return None

def get_weather_forecast_sync(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true"
    }
    response = requests.get(url, params=params, timeout=5)
    if response.status_code == 200:
        return response.json()
    return None

async def run(params: dict):
    location = params.get("location", "").strip()

    if not location:
        yield {"type": "error", "message": "Location/City name is required."}
        return

    yield {"type": "log", "message": f"Querying Geocoding API to resolve coordinates for: '{location}'..."}

    loop = asyncio.get_running_loop()
    coords = await loop.run_in_executor(None, get_coordinates_sync, location)

    if not coords:
        yield {"type": "error", "message": f"Could not find coordinates for city: {location}."}
        return

    name = coords["name"]
    country = coords["country"]
    admin = coords.get("admin1", "")
    lat = coords["latitude"]
    lon = coords["longitude"]

    yield {"type": "log", "message": f"Resolved Location: {name}, {admin} ({country})"}
    yield {"type": "log", "message": f"Coordinates: Lat {lat:.4f}, Lon {lon:.4f}. Querying Open-Meteo Weather forecast..."}

    yield {"type": "progress", "percent": 50.0}

    weather = await loop.run_in_executor(None, get_weather_forecast_sync, lat, lon)

    if not weather or "current_weather" not in weather:
        yield {"type": "error", "message": "Failed to retrieve forecast data."}
        return

    yield {"type": "progress", "percent": 100.0}

    current = weather["current_weather"]
    temp = current.get("temperature")
    wind = current.get("windspeed")
    direction = current.get("winddirection")
    code = current.get("weathercode")

    condition_desc = WMO_CODES.get(code, f"Unknown code {code} ⛅")

    yield {"type": "log", "message": "\nWeather Report Summary:"}
    yield {"type": "log", "message": f"  🌡️ Temperature:   {temp}°C"}
    yield {"type": "log", "message": f"  🌧️ Conditions:    {condition_desc}"}
    yield {"type": "log", "message": f"  💨 Wind Speed:     {wind} km/h (Direction: {direction}°)"}

    yield {"type": "success", "message": f"Current weather in {name}: {temp}°C, {condition_desc}."}
