from datetime import datetime, timedelta
from locations import locations
from location_choice import location_choice, location_menu


def location_choice_recall(input_func=input, output_func=print):
    try:
        import requests
        import pandas as pd
        import matplotlib.pyplot as plt
        from zambretti_py import PressureData, Zambretti
    except ImportError as e:
        output_func(
            "Weather reporting requires optional packages: requests, pandas, matplotlib, zambretti_py."
        )
        output_func("Install them with pip and try again.")
        return None, None

    location_menu(output_func=output_func)
    latitude, longitude = location_choice(input_func=input_func, output_func=output_func)

    end_date = datetime.today()
    start_date = end_date - timedelta(days=1)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_str,
        "end_date": end_str,
        "hourly": "temperature_2m,relativehumidity_2m,surface_pressure,weather_code",
        "timezone": "UTC"
    }

    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data["hourly"])
    df['time'] = pd.to_datetime(df['time'])

    output_func(df.head())

    plt.figure(figsize=(14, 7))
    plt.plot(
        df['time'],
        df['temperature_2m'],
        label='Temperature (°C)',
        color='tomato'
    )
    plt.plot(
        df['time'],
        df['relativehumidity_2m'],
        label='Humidity (%)',
        color='royalblue'
    )
    plt.plot(
        df['time'],
        df['surface_pressure'],
        label='Pressure (hPa)',
        color='seagreen'
    )
    plt.xlabel('Time')
    plt.ylabel('Measurements')
    plt.title('Weather Data Over the Past Day')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    elevation_url = "https://api.open-meteo.com/v1/elevation"
    elevation_params = {"latitude": latitude, "longitude": longitude}
    elevation_response = requests.get(elevation_url, params=elevation_params)
    elevation_data = elevation_response.json()
    elevation = elevation_data.get("elevation")[0]

    if elevation is not None:
        output_func(
            f"The elevation at the location ({latitude}, {longitude}) is {elevation} meters."
        )
    else:
        output_func("Elevation data not available.")

    pressure_data = df[['time', 'surface_pressure']]
    pressure_data.columns = ['timestamp', 'pressure']
    pressure_data = pressure_data.dropna()
    data_points = list(pressure_data.itertuples(index=False, name=None))

    temperature = df['temperature_2m'].iloc[-1]
    output_func(
        f"The last temperature measurement for the location ({latitude}, {longitude}) is: {temperature}°C"
    )
    weathercode = df['weather_code'].iloc[-1]
    output_func(
        f"The weather code for the location ({latitude}, {longitude}) is: {weathercode}"
    )

    pressure_data = PressureData(data_points)
    zambretti = Zambretti()
    forecast = zambretti.forecast(
        elevation=int(elevation),
        temperature=int(temperature),
        pressure_data=pressure_data,
    )

    output_func(
        f"The Zambretti forecast for the location ({latitude}, {longitude}) is: {forecast}"
    )

    return forecast, weathercode
