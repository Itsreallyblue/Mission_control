#this file print telemetry

def show_telemetry(rocket):

    print("\nMISSION TELEMETRY")
    print("-" * 30)
    rocket_name = getattr(rocket, "name", "Unnamed Rocket")
    print(f"Rocket...........{rocket_name}")
    print(f"Fuel.............{rocket.fuel}%")
    print(f"Altitude.........{rocket.altitude} m")
    print(f"Speed............{rocket.speed} m/s")
    print(f"Engine Temp......{rocket.engine_temp}°C")
    print(f"Missions Completed: {rocket.missions_completed}")
    print(f"Engine Status.....{'OK' if rocket.check_engine() else 'Overheating'}")