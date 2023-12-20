import os
from datetime import datetime

import requests


def get_weather(location, date):
    api_key = os.getenv('API_KEY')
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}?unitGroup=metric&include=hours&key={api_key}&contentType=json"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Unexpected status code: {response.status_code}")
        return None

    return response.json().get("days", [])[0]


def degrees_to_cardinal(d):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    ix = round(d / 45)
    return dirs[ix % 8]


def moon_phase_to_text(moon_phase):
    if moon_phase == 0:
        return "new moon 🌑"
    elif 0 < moon_phase < 0.25:
        return "waxing crescent 🌒"
    elif moon_phase == 0.25:
        return "first quarter 🌓"
    elif 0.25 < moon_phase < 0.5:
        return "waxing gibbous 🌔"
    elif moon_phase == 0.5:
        return "full moon 🌕"
    elif 0.5 < moon_phase < 0.75:
        return "waning gibbous 🌖"
    elif moon_phase == 0.75:
        return "last quarter 🌗"
    else:
        return "waning crescent 🌘"


def display_weather_data(location, date, day_data):
    # Define headers title and columns size
    headers = [
        "Time", "Temperature", "Humidity", "Wind", "Gusts", "Direction",
        "Visibility", "Clouds", "UV", "Precipitations", "Conditions"
    ]
    col_widths = [16, 26, 10, 10, 10, 10, 12, 8, 5, 20, 22]

    # Build table
    border_top = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
    border_mid = "├" + "┼".join("─" * w for w in col_widths) + "┤"
    border_bottom = "└" + "┴".join("─" * w for w in col_widths) + "┘"

    # Print informations and headers
    print(f"\n🌃 Town: {location}")
    print(f"📆 Date: {date}")
    print(f"🌆 Sunrise: {day_data.get('sunrise')}")
    print(f"🌇 Sunset: {day_data.get('sunset')}")
    print(f"🌙 Moonphase: {moon_phase_to_text(day_data.get('moonphase'))}")
    print(border_top)
    print("│" + "│".join(
        header.center(width)
        for header, width in zip(headers, col_widths)) + "│")
    print(border_mid)

    # For each hour, print a row with weather informations
    for hour in day_data.get("hours", []):
        hour_time = hour['datetime']
        temperature = f"{hour['temp']}°C (feels like {hour['feelslike']}°C)"
        humidity = f"{hour['humidity']}%"
        wind = f"{hour['windspeed']} km/h"
        gusts = f"{hour['windgust']} km/h"
        direction = degrees_to_cardinal(hour.get('winddir', 0))
        visibility = f"{hour['visibility']} km"
        clouds = f"{hour['cloudcover']}%"
        uv = f"{hour['uvindex']}"
        precipitations = f"{hour['precipprob']}%, {hour['precip']}mm"
        conditions = hour['conditions']

        row = [
            hour_time.center(col_widths[0]),
            temperature.center(col_widths[1]),
            humidity.center(col_widths[2]),
            wind.center(col_widths[3]),
            gusts.center(col_widths[4]),
            direction.center(col_widths[5]),
            visibility.center(col_widths[6]),
            clouds.center(col_widths[7]),
            uv.center(col_widths[8]),
            precipitations.center(col_widths[9]),
            conditions.center(col_widths[10])
        ]
        print("│" + "│".join(row) + "│")

    print(border_bottom)


def calculate_sky_observability_score(hours_data):
    total_score = 0
    num_hours = len(hours_data)

    for hour in hours_data:
        cloud_cover = hour.get('cloudcover', 100)
        visibility = hour.get('visibility', 0)
        wind_speed = hour.get('windspeed', 0)
        humidity = hour.get('humidity', 0)

        cloud_score = (100 - cloud_cover) / 100 * 5

        visibility_score = min(visibility / 10, 1) * 5

        wind_score = (1 - min(wind_speed / 20, 1)) * 5

        humidity_score = (1 - min(humidity / 100, 1)) * 5

        hour_score = cloud_score + visibility_score + wind_score + humidity_score
        total_score += hour_score

    # Average score for all hours, normalized to a scale of 20
    average_score = (total_score / num_hours) * 4
    return round(average_score, 2)


def main():
    location = input("Town: ")
    date_input = input(
        "Date in DD-MM-YYYY format (leave blank for today): ").strip()

    date = date_input if date_input else datetime.today().strftime("%d-%m-%Y")
    date_formatted = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")

    day_data = get_weather(location, date_formatted)

    if day_data:
        display_weather_data(location, date_formatted, day_data)
        # TODO : calculate_sky_observability_score()
    else:
        print("No weather data found for this date or format error.")


if __name__ == "__main__":
    main()
