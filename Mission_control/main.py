#this is the only file that talks to everything else

# initialize logging for the application
import logger_config  # configures file-based logging on import

from rocket import Rocket
from rocket_types import build_rocket, select_rocket_type
from storage import load_rocket_data, reset_save, save_rocket
from telemetry import show_telemetry
from launch import attempt_launch
from weather import get_weather
from refuelstation import refuel_station

data = load_rocket_data()

rocket = Rocket(**data)
rocket.name = "Current Rocket"


def choose_rocket_for_action(current_rocket):
    selected_rocket_type = select_rocket_type(input, print)
    if current_rocket and getattr(current_rocket, "name", None) == selected_rocket_type["name"]:
        return current_rocket

    selected_rocket = build_rocket(selected_rocket_type, current_rocket=current_rocket)
    selected_rocket.name = selected_rocket_type["name"]
    return selected_rocket


while True:

    print("\n" + "=" * 48)
    print("        MISSION CONTROL")
    print("=" * 48)
    print(" 1) Rocket Status        2) Launch Rocket")
    print(" 3) Telemetry            4) Weather Report")
    print(" 5) Save                 6) Reset Save")
    print(" 7) Refuel Station       8) Logging Settings")
    print(" 9) Exit                 L) Open Logging Menu")

    choice = input("\nChoose an option: ").strip()

    if choice in {"1", "2", "3", "5", "6", "7"}:
        rocket = choose_rocket_for_action(rocket)

    if choice == "1":
        rocket.display_status()

    elif choice == "2":
        attempt_launch(rocket)

    elif choice == "3":
        show_telemetry(rocket)

    elif choice == "4":
        print(f"Weather: {get_weather()}")

    elif choice == "5":
        saved = save_rocket(rocket)
        if saved:
            print("Mission saved.")
        else:
            print("Failed to save mission. Check logs.")

    elif choice == "6":
        reset_save_confirm = input("Are you sure you want to reset the save? (y/n): ")
        if reset_save_confirm.lower() == "y":
            reset_save(rocket)
            print("Save reset.")

    elif choice == "7":
        refuel_station(rocket)

    elif choice == "8":
        # Logging settings submenu
        while True:
            print("\nLogging Settings")
            print("1) Set log level (current: %s)" % logger_config.get_log_level())
            print("2) Toggle console logging (currently: %s)" % ("ON" if logger_config.is_console_enabled() else "OFF"))
            print("3) Back")
            sub = input("Choose: ")
            if sub == "1":
                lvl = input("Enter log level (DEBUG, INFO, WARNING, ERROR, CRITICAL): ")
                try:
                    logger_config.set_log_level(lvl)
                    print("Log level set to", logger_config.get_log_level())
                except Exception as e:
                    print("Invalid level:", e)
            elif sub == "2":
                current = logger_config.is_console_enabled()
                logger_config.set_console_enabled(not current)
                print("Console logging now", "ON" if not current else "OFF")
            elif sub == "3":
                break
            else:
                print("Invalid option")

    elif choice.lower() == "l":
        # same logging menu as option 8
        while True:
            print("\nLogging Settings")
            print("1) Set log level (current: %s)" % logger_config.get_log_level())
            print("2) Toggle console logging (currently: %s)" % ("ON" if logger_config.is_console_enabled() else "OFF"))
            print("3) View last N lines of log")
            print("4) Back")
            sub = input("Choose: ")
            if sub == "1":
                lvl = input("Enter log level (DEBUG, INFO, WARNING, ERROR, CRITICAL): ")
                try:
                    logger_config.set_log_level(lvl)
                    print("Log level set to", logger_config.get_log_level())
                except Exception as e:
                    print("Invalid level:", e)
            elif sub == "2":
                current = logger_config.is_console_enabled()
                logger_config.set_console_enabled(not current)
                print("Console logging now", "ON" if not current else "OFF")
            elif sub == "3":
                try:
                    from pathlib import Path
                    log_file = Path(__file__).with_name("logs") / "mission_control.log"
                    n = int(input("How many lines to show from log end? "))
                    if log_file.exists():
                        with log_file.open("r", encoding="utf-8") as f:
                            lines = f.readlines()
                            for line in lines[-n:]:
                                print(line.rstrip())
                    else:
                        print("Log file not found:", log_file)
                except Exception as e:
                    print("Error reading log:", e)
            elif sub == "4":
                break
            else:
                print("Invalid option")

    elif choice == "9":
        print("Goodbye Commander.")
        break

    else:
        print("Invalid option.")