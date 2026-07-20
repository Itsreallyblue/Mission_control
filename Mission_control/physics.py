import time

def simulate_flight(rocket):

    while rocket.fuel > 0:

        rocket.burn_fuel()

        rocket.launch()z

        rocket.display_status()

        time.sleep(1)

        if rocket.altitude >= 10000 or rocket.fuel <= 0 or rocket.fuel == 0:
            break