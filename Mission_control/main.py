#this is the only file that talks to everything else

# initialize logging for the application
import logger_config  # configures file-based logging on import

from rocket import Rocket
from storage import load_rocket_data, reset_save, save_rocket
from telemetry import show_telemetry
from launch import attempt_launch
from weather import get_weather
from refuelstation import refuel_station

data = load_rocket_data()

rocket = Rocket(**data)

while True:

    print("\n" + "=" * 48)
    print("        MISSION CONTROL")
    print("=" * 48)
    print(" 1) Rocket Status        2) Launch Rocket")
    print(" 3) Telemetry            4) Weather Report")
    print(" 5) Save                 6) Reset Save")
    print(" 7) Refuel Station       8) Exit")

    choice = input("\nChoose an option: ")

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
        print("Goodbye Commander.")
        break

    else:
        print("Invalid option.")