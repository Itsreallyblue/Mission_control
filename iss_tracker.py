import requests
import time



def get_iss_location_stage_1():

    url = "http://api.open-notify.org/iss-now.json"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    latitude = float(data["iss_position"]["latitude"])
    longitude = float(data["iss_position"]["longitude"])

    return latitude, longitude


latitude, longitude = get_iss_location_stage_1()


def get_iss_location_stage_2():
   for i in range(5):
       print(f"ISS: {latitude}, {longitude}")
       time.sleep(1)
