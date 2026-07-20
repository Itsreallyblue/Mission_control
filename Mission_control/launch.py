# this file controls the launch
import random
import sys
import time
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from weather import get_weather
from activetelemetry import show_telemetry_persec
from storage import save_rocket

logger = logging.getLogger("mission_control.launch")


def attempt_launch(rocket):
    logger.info("Starting launch sequence for rocket")

    for i in range(5, 0, -1):
        print(f"Launching in T-{i}...")
        time.sleep(1)

    weather = get_weather()
    print(f"\nWeather: {weather}")
    logger.info("Weather: %s", weather)

    if weather == "Storm":
        print("Launch aborted due to storm.")
        logger.warning("Launch aborted: stormy weather")
        return False

    # initial burn and liftoff
    rocket.burn_fuel()
    rocket.launch()
    logger.info("Liftoff: fuel=%s altitude=%s", rocket.fuel, rocket.altitude)
    print("Launch successful!")

    # mission simulation loop: mission time increases, fuel decreases, altitude changes
    mission_duration = random.randint(8, 16)  # seconds for simulation
    rocket.timer = 0
    ascending = True

    for sec in range(mission_duration):
        time.sleep(1)
        rocket.timer += 1

        # fuel consumption each second
        fuel_loss = random.randint(3, 7)
        rocket.fuel = max(0, rocket.fuel - fuel_loss)

        # altitude changes: ascend first half, descend second half
        if rocket.timer <= mission_duration // 2:
            climb = random.randint(100, 300)
            rocket.altitude += climb
        else:
            # indicate return to Earth when entering descent
            if ascending:
                print("Returning to Earth...")
                logger.info("Phase: returning to Earth at t=%ds", rocket.timer)
                ascending = False
            descent = random.randint(80, 250)
            rocket.altitude = max(0, rocket.altitude - descent)

        # log periodic telemetry at DEBUG level (kept out of INFO log files by default)
        logger.debug(
            "t=%ds fuel=%s altitude=%s", rocket.timer, rocket.fuel, rocket.altitude
        )

        # optionally show per-second telemetry if available
        try:
            show_telemetry_persec(rocket)
        except Exception:
            pass

        # abort mission if fuel depleted
        if rocket.fuel <= 0:
            logger.warning("Mission aborted: fuel depleted at t=%ds", rocket.timer)
            print("Mission aborted: fuel depleted.")
            break

    # mission complete, increment missions if not already
    rocket.missions_completed += 1

    # attempt to save mission result
    saved = False
    try:
        saved = save_rocket(rocket)
    except Exception:
        logger.exception("Error saving rocket after mission")

    if saved:
        logger.info(
            "Mission complete: duration=%ds final_fuel=%s final_altitude=%s missions=%s",
            rocket.timer,
            rocket.fuel,
            rocket.altitude,
            rocket.missions_completed,
        )
    else:
        logger.error("Mission complete but failed to save mission data")

    print("Mission complete.")
    return True


def launch(self):
    if not self.check_engine():
        return

    self.altitude += 1000
    self.speed += 200
    self.engine_temp += random.randint(3, 8)
    self.missions_completed += 1
