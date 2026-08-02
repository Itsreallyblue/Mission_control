import time


def get_iss_location_stage_1():
    try:
        import requests
    except ImportError:
        print("ISS tracking requires the optional 'requests' package.")
        print("Install it with pip to enable ISS location tracking.")
        return None, None

    url = "http://api.open-notify.org/iss-now.json"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    latitude = float(data["iss_position"]["latitude"])
    longitude = float(data["iss_position"]["longitude"])

    return latitude, longitude


def get_iss_location_stage_2(latitude, longitude):
    if latitude is None or longitude is None:
        print("ISS location is unavailable because the request failed or the package is missing.")
        return
    for i in range(5):
        print(f"ISS: {latitude}, {longitude}")
        time.sleep(1)
