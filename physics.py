import time

import rocket

def simulate_flight(rocket):

    while rocket.fuel > 0:

        rocket.burn_fuel()

        update_physics(rocket)

        rocket.display_status()

        time.sleep(1)

        if rocket.altitude >= 10000 or rocket.fuel <= 0 or rocket.fuel == 0:
            break


def update_physics(rocket, dt=1.0):
    effective_thrust = rocket.thrust * (rocket.throttle / 100)

    # Atmospheric drag increases with speed, making it harder to escape orbit.
    drag_coefficient = 0.08
    drag_force = drag_coefficient * max(rocket.speed, 0)
    net_force = effective_thrust - rocket.mass * rocket.gravity - drag_force

    rocket.acceleration = net_force / rocket.mass
    rocket.speed += rocket.acceleration * dt

    # Prevent backward movement from overpowering the climb.
    rocket.speed = max(0, rocket.speed)
    rocket.altitude += rocket.speed * dt