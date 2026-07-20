def show_telemetry_persec(rocket):

    print("\nMISSION TELEMETRY")
    print("-" * 30)
    # show fuel, altitude, speed, engine temp, engine status, and mission timer
    print(f"Fuel.............{rocket.fuel}%")
    print(f"Altitude.........{rocket.altitude} m")
    print(f"Speed............{rocket.speed} m/s")
    print(f"Engine Temp......{rocket.engine_temp} C")
    print(f"Engine Status.....{'OK' if rocket.check_engine() else 'Overheating'}")
    # mission timer
    timer = getattr(rocket, "timer", 0)
    if timer:
        hrs = timer // 3600
        mins = (timer % 3600) // 60
        secs = timer % 60
        if hrs:
            timestr = f"{hrs}:{mins:02d}:{secs:02d}"
        else:
            timestr = f"{mins}:{secs:02d}"
        print(f"Mission Time.....{timestr}")
   