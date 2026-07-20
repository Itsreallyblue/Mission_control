import random

weather_conditions = [
    "Clear",
    "Cloudy",
    "Rain",
    "Storm"
]

weather_data = {
    "Clear": 1.0,
    "Cloudy": 0.95,
    "Rain": 0.80,
    "Storm": 0.0
}

def get_weather():

    weather = random.choice(list(weather_data.keys()))

    return weather


def get_weather():
    return random.choice(weather_conditions)