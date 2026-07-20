import time
from rocket import Rocket
from storage import save_rocket

def refuel_station(rocket):
    print("Refueling the rocket...")
    time.sleep(5)
    # ensure we update the Rocket's `fuel` attribute (not `fuel_level`)
    rocket.fuel = 100
    # attempt to persist save immediately after refueling
    saved = save_rocket(rocket)
    if saved:
        print("Rocket refueled to 100% - save successful.")
    else:
        print("Rocket refueled to 100% - failed to save.")