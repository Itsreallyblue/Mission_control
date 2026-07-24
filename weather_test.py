import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from zambretti_py import PressureData, Zambretti
from locations import launchpad_locations





# ----- Define Location and Date Range -----

# Define coordinates (example: London)
latitude = 51.50742
longitude = -0.1278

# Define the date range: last 7 days
end_date = datetime.today()
start_date = end_date - timedelta(days=7)

# Format dates as required by the API (YYYY-MM-DD)
start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")


# ----- Get Weather Data from Open Meteo API -----

# Build the URL and parameters for the Open Meteo API
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": start_str,
    "end_date": end_str,
    "hourly": "temperature_2m,relativehumidity_2m,surface_pressure",
    "timezone": "UTC"
}

# Request the data
response = requests.get(url, params=params)
data = response.json()

# Convert the 'hourly' data to a Pandas DataFrame
df = pd.DataFrame(data["hourly"])

# Convert the time column from string to datetime
df['time'] = pd.to_datetime(df['time'])

# Preview the data
print(df.head())


# ----- Plot Weather Data -----

plt.figure(figsize=(14, 7))
plt.plot(df['time'], df['temperature_2m'], label='Temperature (°C)', color='tomato')
plt.plot(df['time'], df['relativehumidity_2m'], label='Humidity (%)', color='royalblue')
plt.plot(df['time'], df['surface_pressure'], label='Pressure (hPa)', color='seagreen')
plt.xlabel('Time')
plt.ylabel('Measurements')
plt.title('Weather Data Over the Past Week')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ----- Get Elevation Data from Open Meteo Elevation API -----

# Build the URL and parameters for the Open Meteo Elevation API
elevation_url = "https://api.open-meteo.com/v1/elevation"
elevation_params = {
    "latitude": latitude,
    "longitude": longitude
}

# Request the elevation data
elevation_response = requests.get(elevation_url, params=elevation_params)
elevation_data = elevation_response.json()

# Extract the elevation from the response
elevation = elevation_data.get("elevation")[0]
if elevation is not None:
    print(f"The elevation at the location ({latitude}, {longitude}) is {elevation} meters.")
else:
    print("Elevation data not available.")


# ----- Zambretti Forecast -----

# Retrieve pressure data from the DataFrame (time and surface_pressure columns)
pressure_data = df[['time', 'surface_pressure']]
pressure_data.columns = ['timestamp', 'pressure']
pressure_data = pressure_data.dropna()

# Convert the pressure data to a list of tuples
data_points = list(pressure_data.itertuples(index=False, name=None))

# Get last temperature measurement from the DataFrame
temperature = df['temperature_2m'].iloc[-1]
print(f"The last temperature measurement for the location ({latitude}, {longitude}) is: {temperature}°C")

# Create a PressureData object with the retrieved data points
pressure_data = PressureData(
    data_points
)

# Create a Zambretti object and get the forecast
zambretti = Zambretti()
forecast = zambretti.forecast(
    elevation=int(elevation),
    temperature=int(temperature),
    pressure_data=pressure_data,
)

# Return the forecast
print(f"The Zambretti forecast for the location ({latitude}, {longitude}) is: {forecast}")