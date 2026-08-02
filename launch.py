# this file controls the launch
import random
import sys
import time
import logging
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from physics import update_physics
from activetelemetry import show_telemetry_persec
from storage import save_rocket
from weather_test import location_choice_recall
import settings
import logger_config
from flight_computer import evaluate_and_report
import constants

logger = logging.getLogger("mission_control.launch")


def attempt_launch(rocket, input_func=input):
    rocket_name = getattr(rocket, "name", "rocket")
    print(f"Starting launch sequence for {rocket_name}...")

    launch_choice = input_func("Press 1 to continue launch or 2 to abort: ").strip()
    if launch_choice == "2":
        print("Launch aborted by user.")
        logger.info("Launch aborted by user")
        return False
    if launch_choice != "1":
        print("Invalid choice. Launch aborted.")
        logger.info("Launch aborted due to invalid confirmation")
        return False

    forecast, weathercode = location_choice_recall(input_func=input_func, output_func=print)

    for i in range(constants.LAUNCH_COUNTDOWN_SECONDS, 0, -1):
        print(f"Launching in T-{i}...")
        time.sleep(1)

    print(f"\nWeather: {forecast}")
    logger.debug("Weather: %s", forecast)

    dangerous_weather = ["75", "73", "77", "82", "86", "95", "96", "99"]

    if str(weathercode) in dangerous_weather:
        print("Launch aborted due to dangerous weather.")
        logger.warning("Launch aborted: dangerous weather")
        return False

    rocket.burn_fuel()
    update_physics(rocket)
    print("Launch successful! Liftoff!")
    logger.debug("Liftoff: fuel=%s altitude=%s", rocket.fuel, rocket.altitude)

    mission_id = f"mission-{time.strftime('%Y%m%d-%H%M%S')}-{random.randint(1000, 9999)}"
    mission_duration = random.randint(constants.LAUNCH_MIN_DURATION, constants.LAUNCH_MAX_DURATION)
    rocket.timer = 0
    ascending = True
    max_altitude = 0
    top_speed = 0
    mission_success = False
    escape_orbit = False
    times = []
    fuels = []
    alts = []
    accels = []

    for sec in range(mission_duration):
        time.sleep(1)
        rocket.timer += 1
        prev_speed = getattr(rocket, "speed", 0)
        fuel_loss = random.randint(3, 7)
        rocket.fuel = max(0, rocket.fuel - fuel_loss)

        if rocket.timer <= mission_duration // 2:
            climb = random.randint(100, 300)
            rocket.altitude += climb
            rocket.speed += random.randint(5, 15)
        else:
            if ascending:
                print("Returning to Earth...")
                logger.debug("Phase: returning to Earth at t=%ds", rocket.timer)
                ascending = False
            descent = random.randint(80, 250)
            rocket.altitude = max(0, rocket.altitude - descent)
            rocket.speed = max(0, rocket.speed - random.randint(3, 10))

        rocket.engine_temp += rocket.throttle * constants.ENGINE_HEAT_RATE_PER_THROTTLE

        assessment = evaluate_and_report(rocket)
        if assessment["should_shutdown_engines"]:
            logger.warning("Flight computer triggered shutdown for %s", getattr(rocket, "name", "rocket"))
            print("Mission aborted by flight computer.")
            break

        if rocket.engine_temp > constants.ENGINE_OVERHEAT_THRESHOLD_C:
            print("ENGINE OVERHEAT! Mission aborted.")
            logger.warning("Engine overheat for %s at %s°C", getattr(rocket, "name", "rocket"), rocket.engine_temp)
            break

        max_altitude = max(max_altitude, rocket.altitude)
        top_speed = max(top_speed, rocket.speed)

        if rocket.altitude >= constants.ESCAPE_ALTITUDE_M:
            escape_velocity = constants.ESCAPE_VELOCITY_BASE_M_PER_S * (1.0 + (rocket.altitude / 100000.0)) ** 0.5
            if rocket.speed >= escape_velocity:
                escape_orbit = True
                print("ESCAPE ORBIT ACHIEVED! The rocket has escaped orbit.")
                logger.info("Escape orbit achieved for %s", getattr(rocket, "name", "rocket"))
                break

        accel = rocket.speed - prev_speed
        rocket.acceleration = accel
        try:
            logger_config.write_plain_log(f"t={rocket.timer}s fuel={rocket.fuel} altitude={rocket.altitude} accel={accel}")
        except Exception:
            logger.debug(
                "t=%ds fuel=%s altitude=%s accel=%s", rocket.timer, rocket.fuel, rocket.altitude, accel
            )

        try:
            show_telemetry_persec(rocket)
        except Exception:
            pass

        times.append(rocket.timer)
        fuels.append(rocket.fuel)
        alts.append(rocket.altitude)
        accels.append(getattr(rocket, "acceleration", 0))

        if rocket.fuel <= 0:
            logger.warning("Mission aborted: fuel depleted at t=%ds", rocket.timer)
            print("Mission aborted: fuel depleted.")
            break

    rocket.missions_completed += 1
    mission_success = escape_orbit and rocket.fuel > 0

    print("\n=== MISSION REPORT ===")
    print(f"Mission ID: {mission_id}")
    print(f"Rocket: {getattr(rocket, 'name', 'Unnamed Rocket')}")
    print(f"Mission Time: {rocket.timer}s")
    print(f"Max Altitude: {max_altitude:.2f} m")
    print(f"Top Speed: {top_speed:.2f} m/s")
    print(f"Remaining Fuel: {rocket.fuel:.2f}%")
    print(f"Mission Success: {'Yes' if mission_success else 'No'}")
    print("======================")

    if mission_success:
        logger.info("Mission report: id=%s rocket=%s success=yes", mission_id, getattr(rocket, "name", "Unnamed Rocket"))
    else:
        logger.info("Mission report: id=%s rocket=%s success=no", mission_id, getattr(rocket, "name", "Unnamed Rocket"))

    def ascii_plot(title, times, values, max_width=settings.ASCII_MAX_WIDTH):
        if not times:
            return
        print(f"\n{title}")
        max_val = max(values)
        min_val = min(values)
        span = max_val - min_val if max_val != min_val else 1
        for t, v in zip(times, values):
            bar_len = int((v - min_val) / span * max_width)
            print(f"{t:>3}s | {v:>6} | " + "#" * bar_len)

    plot_names = {}

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        try:
            plt.style.use(settings.PLOT_STYLE)
        except Exception:
            pass

        plots_base_dir = settings.PLOTS_DIR
        mission_date = time.strftime("%Y-%m-%d")
        plots_dir = plots_base_dir / mission_date
        plots_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fig_path = plots_dir / f"mission_{timestamp}.png"

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
        ax1.plot(times, fuels, marker='o')
        ax1.set_ylabel('Fuel (%)')
        ax1.set_title('Fuel vs Time')
        ax1.grid(True)

        ax2.plot(times, alts, marker='o', color='orange')
        ax2.set_ylabel('Altitude (m)')
        ax2.grid(True)

        ax3.plot(times, accels, marker='o', color='green')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Acceleration (m/s^2)')
        ax3.grid(True)

        fig.tight_layout()
        fig.savefig(fig_path)
        plot_names['mission_plot'] = str(fig_path)
    except Exception:
        pass

    if plot_names:
        print("Mission plot saved:")
        for name, path in plot_names.items():
            print(f" - {name}: {path}")
