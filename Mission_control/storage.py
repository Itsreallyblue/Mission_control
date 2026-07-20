#this file is responsible for loading and saving

import json
import logging
import time
from pathlib import Path

SAVE_FILE = Path(__file__).with_name("rocket.json")


def load_rocket_data():

    if SAVE_FILE.exists():

        with SAVE_FILE.open("r") as file:
            return json.load(file)

    return {
        "fuel": 100,
        "speed": 0,
        "altitude": 0,
        "missions_completed": 0,
        "engine_temp": 25,
        "timer": 0
    }


def save_rocket(rocket):

    data = {
        "fuel": rocket.fuel,
        "speed": rocket.speed,
        "altitude": rocket.altitude,
        "missions_completed": rocket.missions_completed,
        "engine_temp": rocket.engine_temp,
        "timer": getattr(rocket, "timer", 0)
    }
    logger = logging.getLogger("mission_control.storage")
    temp_file = SAVE_FILE.with_name(SAVE_FILE.name + ".tmp")
    max_retries = 3
    backoff = 0.2
    for attempt in range(1, max_retries + 1):
        try:
            with temp_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            # atomic replace
            temp_file.replace(SAVE_FILE)
            # log only the filename for readability at DEBUG level
            logger.debug("Save successful: %s", SAVE_FILE.name)
            return True
        except Exception as e:
            logger.exception("Attempt %d: Error saving rocket data: %s", attempt, e)
            # cleanup temp file if present
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass
            if attempt < max_retries:
                time.sleep(backoff * attempt)
            else:
                logger.error("Failed to save rocket data after %d attempts.", max_retries)
                return False

def reset_save(rocket):

    data = {
        "fuel": 100,
        "speed": 0,
        "altitude": 0,
        "missions_completed": 0,
        "engine_temp": 25,
        "timer": 0
    }

    # Update the rocket object with default values
    rocket.fuel = data["fuel"]
    rocket.speed = data["speed"]
    rocket.altitude = data["altitude"]
    rocket.missions_completed = data["missions_completed"]
    rocket.engine_temp = data["engine_temp"]
    rocket.timer = data.get("timer", 0)

    with SAVE_FILE.open("w") as file:
        json.dump(data, file, indent=4)