from rocket import Rocket

ROCKET_TYPES = [
    {
        "name": "Falcon 9",
        "description": "Reliable workhorse for orbital missions",
        "defaults": {
            "fuel": 100,
            "speed": 0,
            "altitude": 0,
            "missions_completed": 0,
            "engine_temp": 25,
            "timer": 0,
            "acceleration": 0,
            "mass": 500,
            "thrust": 15000,
            "gravity": 9.81,
            "throttle": 100,
        },
    },
    {
        "name": "Starship",
        "description": "Heavy-lift rocket with strong thrust",
        "defaults": {
            "fuel": 120,
            "speed": 0,
            "altitude": 0,
            "missions_completed": 0,
            "engine_temp": 25,
            "timer": 0,
            "acceleration": 0,
            "mass": 700,
            "thrust": 22000,
            "gravity": 9.81,
            "throttle": 100,
        },
    },
    {
        "name": "Saturn V",
        "description": "Classic moon rocket with high payload capacity",
        "defaults": {
            "fuel": 95,
            "speed": 0,
            "altitude": 0,
            "missions_completed": 0,
            "engine_temp": 25,
            "timer": 0,
            "acceleration": 0,
            "mass": 650,
            "thrust": 18000,
            "gravity": 9.81,
            "throttle": 100,
        },
    },
]


def select_rocket_type(input_func=input, output_func=print):
    output_func("\nAvailable rockets:")
    for index, rocket_type in enumerate(ROCKET_TYPES, start=1):
        output_func(f"{index}) {rocket_type['name']} - {rocket_type['description']}")

    while True:
        choice = input_func("Choose a rocket by number: ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(ROCKET_TYPES):
                return ROCKET_TYPES[index]
        output_func("Invalid selection. Please choose one of the rockets above.")


def build_rocket(rocket_type, current_rocket=None):
    rocket = Rocket(**rocket_type["defaults"])
    if current_rocket is not None:
        for attr in (
            "fuel",
            "speed",
            "altitude",
            "missions_completed",
            "engine_temp",
            "timer",
            "acceleration",
            "mass",
            "thrust",
            "gravity",
            "throttle",
        ):
            if hasattr(current_rocket, attr):
                setattr(rocket, attr, getattr(current_rocket, attr))
    rocket.name = rocket_type["name"]
    return rocket

