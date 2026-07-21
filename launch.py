# this file controls the launch
import random
import sys
import time
import logging
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from physics import update_physics
from weather import get_weather
from activetelemetry import show_telemetry_persec
from storage import save_rocket
import settings
import logger_config
from flight_computer import evaluate_and_report
import constants

logger = logging.getLogger("mission_control.launch")


def attempt_launch(rocket):
    rocket_name = getattr(rocket, "name", "rocket")
    # user-facing start message (no logger timestamp)
    print(f"Starting launch sequence for {rocket_name}...")

    launch_choice = input("Press 1 to continue launch or 2 to abort: ").strip()
    if launch_choice == "2":
        print("Launch aborted by user.")
        logger.info("Launch aborted by user")
        return False
    if launch_choice != "1":
        print("Invalid choice. Launch aborted.")
        logger.info("Launch aborted due to invalid confirmation")
        return False

    for i in range(constants.LAUNCH_COUNTDOWN_SECONDS, 0, -1):
        print(f"Launching in T-{i}...")
        time.sleep(1)

    weather = get_weather()
    print(f"\nWeather: {weather}")
    # keep weather in debug logs only to avoid INFO-level noise
    logger.debug("Weather: %s", weather)

    if weather == "Storm":
        print("Launch aborted due to storm.")
        logger.warning("Launch aborted: stormy weather")
        return False

    # initial burn and liftoff
    rocket.burn_fuel()
    update_physics(rocket)
    # user-facing liftoff message without logger timestamp
    print("Launch successful! Liftoff!")
    # detailed liftoff info at DEBUG level
    logger.debug("Liftoff: fuel=%s altitude=%s", rocket.fuel, rocket.altitude)

    # mission simulation loop: mission time increases, fuel decreases, altitude changes
    mission_id = f"mission-{time.strftime('%Y%m%d-%H%M%S')}-{random.randint(1000, 9999)}"
    mission_duration = random.randint(constants.LAUNCH_MIN_DURATION, constants.LAUNCH_MAX_DURATION)  # seconds for simulation
    rocket.timer = 0
    ascending = True
    max_altitude = 0
    top_speed = 0
    mission_success = False
    escape_orbit = False
    # prepare time-series for plotting
    times = []
    fuels = []
    alts = []
    accels = []

    for sec in range(mission_duration):
        time.sleep(1)
        rocket.timer += 1
        # simulate speed change to compute acceleration
        prev_speed = getattr(rocket, "speed", 0)
        # fuel consumption each second
        fuel_loss = random.randint(3, 7)
        rocket.fuel = max(0, rocket.fuel - fuel_loss)

        # altitude changes: ascend first half, descend second half
        if rocket.timer <= mission_duration // 2:
            climb = random.randint(100, 300)
            rocket.altitude += climb
            # increase speed slightly while ascending
            rocket.speed += random.randint(5, 15)
        else:
            # indicate return to Earth when entering descent
            if ascending:
                print("Returning to Earth...")
                # record phase change at DEBUG level to avoid INFO timestamp in console
                logger.debug("Phase: returning to Earth at t=%ds", rocket.timer)
                ascending = False
            descent = random.randint(80, 250)
            rocket.altitude = max(0, rocket.altitude - descent)
            # decrease speed slightly while descending
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

        # compute acceleration (m/s^2) as change in speed per second
        accel = rocket.speed - prev_speed
        rocket.acceleration = accel
        # write per-second telemetry as a plain line (no timestamp/level)
        try:
            logger_config.write_plain_log(f"t={rocket.timer}s fuel={rocket.fuel} altitude={rocket.altitude} accel={accel}")
        except Exception:
            # fallback to debug log if plain write fails
            logger.debug(
                "t=%ds fuel=%s altitude=%s accel=%s", rocket.timer, rocket.fuel, rocket.altitude, accel
            )

        # optionally show per-second telemetry if available
        try:
            show_telemetry_persec(rocket)
        except Exception:
            pass

        # record time-series data for plotting
        times.append(rocket.timer)
        fuels.append(rocket.fuel)
        alts.append(rocket.altitude)
        accels.append(getattr(rocket, "acceleration", 0))

        # abort mission if fuel depleted
        if rocket.fuel <= 0:
            logger.warning("Mission aborted: fuel depleted at t=%ds", rocket.timer)
            print("Mission aborted: fuel depleted.")
            break

    # mission complete, increment missions if not already
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

    # generate plots for fuel vs time, altitude vs time, and acceleration vs time
    def ascii_plot(title, times, values, max_width=settings.ASCII_MAX_WIDTH):
        if not times:
            return
        print(f"\n{title}")
        max_val = max(values)
        min_val = min(values)
        span = max_val - min_val if max_val != min_val else 1
        for t, v in zip(times, values):
            # scale to bar width
            bar_len = int((v - min_val) / span * max_width)
            print(f"{t:>3}s | {v:>6} | " + "#" * bar_len)

    # track saved plot filenames to include in mission summary
    plot_names = {}

    try:
        import matplotlib  # type: ignore[import-not-found]
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt  # type: ignore[import-not-found]

        # apply style if available
        try:
            plt.style.use(settings.PLOT_STYLE)
        except Exception:
            pass

        # ensure output directory organized by mission date
        plots_base_dir = settings.PLOTS_DIR
        mission_date = time.strftime("%Y-%m-%d")
        plots_dir = plots_base_dir / mission_date
        plots_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fig_path = plots_dir / f"mission_{timestamp}.png"

        # create figure with three subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
        ax1.plot(times, fuels, marker='o')
        ax1.set_ylabel('Fuel (%)')
        ax1.set_title('Fuel vs Time')
        ax1.grid(True)

        ax2.plot(times, alts, marker='o', color='orange')
        ax2.set_ylabel('Altitude (m)')
        ax2.set_title('Altitude vs Time')
        ax2.grid(True)

        ax3.plot(times, accels, marker='o', color='green')
        ax3.set_ylabel('Acceleration (m/s^2)')
        ax3.set_xlabel('Time (s)')
        ax3.set_title('Acceleration vs Time')
        ax3.grid(True)

        fig.tight_layout()
        fig.savefig(fig_path)
        plot_names['combined'] = fig_path.name
        # write a plain post-mission line (no timestamp/level prefix)
        try:
            logger_config.write_plain_log(f"Saved mission plots: {fig_path.name}")
        except Exception:
            logger.info("Saved mission plots: %s", fig_path.name)

        # optionally save separate PNGs for each metric
        if getattr(settings, "SAVE_SEPARATE_PLOTS", False):
            try:
                fuel_path = plots_dir / f"mission_{timestamp}_fuel.png"
                alt_path = plots_dir / f"mission_{timestamp}_altitude.png"
                accel_path = plots_dir / f"mission_{timestamp}_accel.png"

                fig_fuel, ax = plt.subplots(1, 1, figsize=(8, 3))
                ax.plot(times, fuels, marker='o', color=settings.PLOT_COLORS.get('fuel'))
                ax.set_ylabel('Fuel (%)')
                ax.set_title('Fuel vs Time')
                ax.grid(True)
                fig_fuel.tight_layout()
                fig_fuel.savefig(fuel_path)
                plot_names['fuel'] = fuel_path.name
                fig_fuel.clf()

                fig_alt, ax = plt.subplots(1, 1, figsize=(8, 3))
                ax.plot(times, alts, marker='o', color=settings.PLOT_COLORS.get('altitude'))
                ax.set_ylabel('Altitude (m)')
                ax.set_title('Altitude vs Time')
                ax.grid(True)
                fig_alt.tight_layout()
                fig_alt.savefig(alt_path)
                plot_names['altitude'] = alt_path.name
                fig_alt.clf()

                fig_acc, ax = plt.subplots(1, 1, figsize=(8, 3))
                ax.plot(times, accels, marker='o', color=settings.PLOT_COLORS.get('accel'))
                ax.set_ylabel('Acceleration (m/s^2)')
                ax.set_title('Acceleration vs Time')
                ax.grid(True)
                fig_acc.tight_layout()
                fig_acc.savefig(accel_path)
                plot_names['accel'] = accel_path.name
                fig_acc.clf()

                try:
                    logger_config.write_plain_log(
                        f"Saved separate mission plots: {fuel_path.name}, {alt_path.name}, {accel_path.name}"
                    )
                except Exception:
                    logger.info("Saved separate mission plots: %s, %s, %s", fuel_path.name, alt_path.name, accel_path.name)
            except Exception:
                logger.exception("Failed to save separate metric plots")

        # try to open the combined image for the user (Windows-friendly)
        if settings.OPEN_PLOT:
            try:
                if os.name == 'nt':
                    os.startfile(str(fig_path))
                else:
                    import webbrowser

                    webbrowser.open(str(fig_path))
            except Exception:
                pass
    except Exception as exc:
        logger.info("Matplotlib unavailable; falling back to ASCII plots: %s", exc)
        # ASCII fallback
        ascii_plot('Fuel vs Time', times, fuels)
        ascii_plot('Altitude vs Time', times, alts)
        ascii_plot('Acceleration vs Time', times, accels)

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
        # append mission time-series and summary to missions log
        try:
            missions_file = settings.MISSIONS_FILE
            missions_file.parent.mkdir(parents=True, exist_ok=True)
            summary = {
                "mission_id": mission_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "rocket_name": getattr(rocket, "name", "Unnamed Rocket"),
                "duration_s": rocket.timer,
                "max_altitude": max_altitude,
                "top_speed": top_speed,
                "final_fuel": rocket.fuel,
                "final_altitude": rocket.altitude,
                "missions_completed": rocket.missions_completed,
                "mission_success": mission_success,
                "escaped_orbit": escape_orbit,
                "times": times,
                "fuels": fuels,
                "altitudes": alts,
                "accelerations": accels,
                "plots": plot_names,
            }
            import json

            with missions_file.open("a", encoding="utf-8") as mf:
                mf.write(json.dumps(summary) + "\n")
            # append an unformatted notice to the main log as well
            try:
                logger_config.write_plain_log(f"Appended mission summary to {missions_file.name}")
            except Exception:
                logger.info("Appended mission summary to %s", missions_file.name)
        except Exception:
            logger.exception("Failed to write mission summary to missions log")
    else:
        logger.error("Mission complete but failed to save mission data")

    print("Mission complete.")
    return True


# end of file
    