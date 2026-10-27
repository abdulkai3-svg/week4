import csv
import json
from getpass import getpass
from pathlib import Path

import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"
CSV_FILE = Path(__file__).with_name("city_data.csv")
HEADERS = ["City", "Country", "Temperature (C)", "Humidity (%)", "Description"]


def get_city():
    """Ask the user for a city name."""
    while True:
        city = input("Enter a city name: ").strip()
        if city:
            return city
        print("Please enter a city name.")


def get_weather(city, api_key):
    """Get current weather information from the API."""
    try:
        response = requests.get(
            API_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )

        if response.status_code == 404:
            print("City not found. Please check the spelling.")
            return None

        if response.status_code == 401:
            print("Invalid or inactive API key.")
            return None

        if response.status_code == 429:
            print("Too many requests. Please try again later.")
            return None

        response.raise_for_status()

        # Convert the API response into Python data.
        data = json.loads(response.text)

        return {
            "City": data["name"],
            "Country": data["sys"]["country"],
            "Temperature (C)": data["main"]["temp"],
            "Humidity (%)": data["main"]["humidity"],
            "Description": data["weather"][0]["description"],
        }

    except requests.RequestException:
        print("Could not get weather information. Check your connection.")
    except (ValueError, KeyError, IndexError, TypeError):
        print("The API returned unexpected weather data.")

    return None


def save_weather(weather):
    """Save weather information into a CSV file."""
    file_has_data = CSV_FILE.exists() and CSV_FILE.stat().st_size > 0

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)

        if not file_has_data:
            writer.writeheader()

        writer.writerow(weather)


def show_saved_cities():
    """Read the CSV file and display saved cities."""
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        cities = list(reader)

    print(f"\nNumber of cities saved: {len(cities)}")

    for city in cities:
        print(
            f"{city['City']}: "
            f"{city['Temperature (C)']} degrees Celsius"
        )


def main():
    """Run the weather report program."""
    city = get_city()
    api_key = getpass("Enter your OpenWeatherMap API key: ").strip()

    if not api_key:
        print("An API key is required.")
        return

    weather = get_weather(city, api_key)

    if weather is None:
        return

    print(f"\nWeather Report for {weather['City']}, {weather['Country']}")
    print(f"Temperature: {weather['Temperature (C)']} degrees Celsius")
    print(f"Humidity: {weather['Humidity (%)']}%")
    print(f"Description: {weather['Description']}")

    try:
        save_weather(weather)
        print("\nWeather saved to city_data.csv")
        show_saved_cities()
    except OSError:
        print("Could not save or read city_data.csv.")


if __name__ == "__main__":
    main()