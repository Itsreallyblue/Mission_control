# this is the only file that talks to everything else
# initialize logging for the application
import logger_config  # configures file-based logging on import
from rocket import Rocket
from rocket_types import build_rocket, select_rocket_type
from storage import load_rocket_data, reset_save, save_rocket
from telemetry import show_telemetry
from launch import attempt_launch
from weather_test import location_choice_recall
from refuelstation import refuel_station
from iss_tracker import get_iss_location_stage_1, get_iss_location_stage_2
import voice_control as vc

VOICE_WAKE_WORD = "commander"


def ask_text(prompt, use_voice=False):
    if use_voice:
        try:
            return vc.get_voice_command(prompt, wake_word=VOICE_WAKE_WORD)
        except Exception as error:
            print("Voice capture failed:", error)
    return input(prompt)


def ask_yes_no(prompt, use_voice=False):
    if use_voice:
        while True:
            command = ask_text(prompt, use_voice=True)
            answer = vc.parse_yes_no(command)
            if answer is None:
                print("Please say yes or no.")
                continue
            return answer
    while True:
        response = input(prompt).strip().lower()
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print("Please enter y or n.")


def ask_number(prompt, use_voice=False, default=None):
    if use_voice:
        while True:
            command = ask_text(prompt, use_voice=True)
            number = vc.parse_int(command)
            if number is not None:
                return number
            print("I didn't understand the number. Please say it again.")
    while True:
        response = input(prompt).strip()
        if response.isdigit():
            return int(response)
        if default is not None and not response:
            return default
        print("Please enter a valid number.")


def parse_main_choice(command):
    if command is None:
        return None
    value = command.strip().lower()
    if not value:
        return None
    choices = {
        "1": "1",
        "one": "1",
        "rocket status": "1",
        "status": "1",
        "2": "2",
        "two": "2",
        "launch rocket": "2",
        "launch": "2",
        "3": "3",
        "three": "3",
        "telemetry": "3",
        "4": "4",
        "four": "4",
        "weather report": "4",
        "weather": "4",
        "5": "5",
        "five": "5",
        "save": "5",
        "6": "6",
        "six": "6",
        "reset save": "6",
        "reset": "6",
        "7": "7",
        "seven": "7",
        "refuel station": "7",
        "refuel": "7",
        "8": "8",
        "eight": "8",
        "logging settings": "8",
        "logging": "8",
        "l": "l",
        "log menu": "l",
        "track iss location": "t",
        "track iss": "t",
        "track": "t",
        "t": "t",
        "9": "9",
        "nine": "9",
        "exit": "9",
        "quit": "9",
        "goodbye": "9",
    }
    if value in choices:
        return choices[value]
    for keyword, result in [
        ("status", "1"),
        ("launch", "2"),
        ("telemetry", "3"),
        ("weather", "4"),
        ("save", "5"),
        ("reset", "6"),
        ("refuel", "7"),
        ("log", "8"),
        ("track", "t"),
        ("exit", "9"),
        ("quit", "9"),
    ]:
        if keyword in value:
            return result
    return None


def parse_logging_choice(command, show_view=False):
    if command is None:
        return None
    value = command.strip().lower()
    if not value:
        return None
    if value in {"1", "one", "set log level", "log level", "set level"}:
        return "1"
    if value in {"2", "two", "toggle console", "console", "toggle console logging"}:
        return "2"
    if show_view and value in {"3", "three", "view", "view log", "view logs", "show log"}:
        return "3"
    if value in {"4", "four", "back", "return", "cancel"}:
        return "4"
    if value in {"3", "three"} and not show_view:
        return "3"
    for keyword, result in [
        ("set", "1"),
        ("toggle", "2"),
        ("view", "3"),
        ("show", "3"),
        ("back", "4"),
    ]:
        if keyword in value:
            return result
    return None


def get_choice(prompt, parser=None, use_voice=False):
    if use_voice:
        while True:
            command = ask_text(prompt, use_voice=True)
            if parser:
                parsed = parser(command)
                if parsed is not None:
                    return parsed
                print("I didn't understand that command. Please say the menu choice again.")
            else:
                return command.strip()
    return input(prompt).strip()


def choose_rocket_for_action(current_rocket, use_voice=False):
    if use_voice:
        def voice_input(prompt):
            return ask_text(prompt, use_voice=True)

        selected_rocket_type = select_rocket_type(voice_input, print)
    else:
        selected_rocket_type = select_rocket_type(input, print)

    if current_rocket and getattr(current_rocket, "name", None) == selected_rocket_type["name"]:
        return current_rocket

    selected_rocket = build_rocket(selected_rocket_type, current_rocket=current_rocket)
    selected_rocket.name = selected_rocket_type["name"]
    return selected_rocket


def logging_menu(use_voice=False, allow_view=False):
    while True:
        print("\nLogging Settings")
        print("1) Set log level (current: %s)" % logger_config.get_log_level())
        print("2) Toggle console logging (currently: %s)" % ("ON" if logger_config.is_console_enabled() else "OFF"))
        if allow_view:
            print("3) View last N lines of log")
            print("4) Back")
        else:
            print("3) Back")

        sub = get_choice("Choose: ", parser=lambda c: parse_logging_choice(c, show_view=allow_view), use_voice=use_voice)

        if sub == "1":
            lvl = ask_text("Enter log level (DEBUG, INFO, WARNING, ERROR, CRITICAL): ", use_voice=use_voice)
            try:
                logger_config.set_log_level(lvl)
                print("Log level set to", logger_config.get_log_level())
            except Exception as e:
                print("Invalid level:", e)
        elif sub == "2":
            current = logger_config.is_console_enabled()
            logger_config.set_console_enabled(not current)
            print("Console logging now", "ON" if not current else "OFF")
        elif sub == "3" and allow_view:
            try:
                from pathlib import Path
                log_file = Path(__file__).with_name("logs") / "mission_control.log"
                n = ask_number("How many lines to show from log end? ", use_voice=use_voice, default=10)
                if log_file.exists():
                    with log_file.open("r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for line in lines[-n:]:
                            print(line.rstrip())
                else:
                    print("Log file not found:", log_file)
            except Exception as e:
                print("Error reading log:", e)
        elif sub == "3" and not allow_view:
            break
        elif sub == "4" and allow_view:
            break
        else:
            print("Invalid option")


data = load_rocket_data()
rocket = Rocket(**data)
rocket.name = "Current Rocket"

voice_enabled = ask_yes_no("Enable voice recognition? (y/n): ")
if voice_enabled:
    wake_word = input(f"Enter wake word or press Enter to use '{VOICE_WAKE_WORD}': ").strip()
    if wake_word:
        VOICE_WAKE_WORD = wake_word

while True:
    print("\n" + "=" * 48)
    print("        MISSION CONTROL")
    print("=" * 48)
    selected_name = getattr(rocket, "name", "Current Rocket")
    print(f"Selected Rocket: {selected_name}")
    print(" 1) Rocket Status        2) Launch Rocket")
    print(" 3) Telemetry            4) Weather Report")
    print(" 5) Save                 6) Reset Save")
    print(" 7) Refuel Station       8) Logging Settings")
    print(" 9) Exit                 L) Open Logging Menu")
    print(" T) Track ISS location")

    choice = get_choice("Choose an option: ", parser=parse_main_choice, use_voice=voice_enabled)

    if choice in {"1", "2", "3", "5", "6", "7"}:
        rocket = choose_rocket_for_action(rocket, use_voice=voice_enabled)

    if choice == "1":
        rocket.display_status()
    elif choice == "2":
        attempt_launch(
            rocket,
            input_func=lambda prompt: ask_text(prompt, use_voice=voice_enabled),
            output_func=print,
        )
    elif choice == "3":
        show_telemetry(rocket)
    elif choice == "4":
        location_choice_recall(
            input_func=lambda prompt: ask_text(prompt, use_voice=voice_enabled),
            output_func=print,
        )
    elif choice == "5":
        saved = save_rocket(rocket)
        if saved:
            print("Mission saved.")
        else:
            print("Failed to save mission. Check logs.")
    elif choice == "6":
        confirmed = ask_yes_no("Are you sure you want to reset the save? (y/n): ", use_voice=voice_enabled)
        if confirmed:
            reset_save(rocket)
            print("Save reset.")
    elif choice == "7":
        refuel_station(rocket)
    elif choice == "8":
        logging_menu(use_voice=voice_enabled, allow_view=False)
    elif isinstance(choice, str) and choice.lower() == "l":
        logging_menu(use_voice=voice_enabled, allow_view=True)
    elif isinstance(choice, str) and choice.lower() == "t":
        latitude, longitude = get_iss_location_stage_1()
        get_iss_location_stage_2(latitude, longitude)
    elif choice == "9":
        print("Goodbye Commander.")
        break
    else:
        print("Invalid option.")
