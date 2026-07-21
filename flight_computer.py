def is_fuel_low(rocket):
    return getattr(rocket, "fuel", 0) <= 20


def is_altitude_dangerous(rocket):
    return getattr(rocket, "altitude", 0) >= 10000


def should_shutdown_engines(rocket):
    return is_fuel_low(rocket) or is_altitude_dangerous(rocket)


def should_warn_pilot(rocket):
    return should_shutdown_engines(rocket)


def assess_flight_conditions(rocket):
    return {
        "is_fuel_low": is_fuel_low(rocket),
        "is_altitude_dangerous": is_altitude_dangerous(rocket),
        "should_shutdown_engines": should_shutdown_engines(rocket),
        "should_warn_pilot": should_warn_pilot(rocket),
    }


def evaluate_and_report(rocket, print_func=print):
    assessment = assess_flight_conditions(rocket)

    print_func("\n[FLIGHT COMPUTER ASSESSMENT]")
    print_func("-" * 30)
    print_func(f"Is fuel low? {'Yes' if assessment['is_fuel_low'] else 'No'}")
    print_func(f"Is altitude dangerous? {'Yes' if assessment['is_altitude_dangerous'] else 'No'}")
    print_func(f"Should the engines shut down? {'Yes' if assessment['should_shutdown_engines'] else 'No'}")
    print_func(f"Should we warn the pilot? {'Yes' if assessment['should_warn_pilot'] else 'No'}")

    return assessment
