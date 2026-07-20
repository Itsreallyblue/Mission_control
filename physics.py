import time

def simulate_flight(rocket):

    while rocket.fuel > 0:

        rocket.burn_fuel()

        rocket.launch()

        rocket.display_status()

        time.sleep(1)

        if rocket.altitude >= 10000 or rocket.fuel <= 0 or rocket.fuel == 0:
            break


def update_physics(rocket, dt=1.0):
    rocket.acceleration = (rocket.thrust / rocket.mass) - rocket.gravity

    rocket.speed += rocket.acceleration * dt

    rocket.altitude += rocket.speed * dt