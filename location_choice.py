from locations import locations


def location_menu(output_func=print):
    output_func("" + "=" * 48)
    output_func("          LAUNCHPAD LOCATIONS")
    output_func("=" * 48)
    output_func(" 1) SaxaVord Spaceport          2) Sutherland Spaceport")
    output_func(" 3) Pacific Spaceport Complex   4) Mahia Launch Complex")
    output_func("")
    output_func("")


def location_choice(input_func=input, output_func=print):
    user_input = input_func("Please choose a number to select a launch location: ")
    choice = user_input.strip().lower()

    if choice == "1":
        output_func(locations[0]["description"])
        latitude = locations[0]["latitude"]
        longitude = locations[0]["longitude"]

    elif choice == "2":
        output_func(locations[1]["description"])
        latitude = locations[1]["latitude"]
        longitude = locations[1]["longitude"]

    elif choice == "3":
        output_func(locations[2]["description"])
        latitude = locations[2]["latitude"]
        longitude = locations[2]["longitude"]

    elif choice == "4":
        output_func(locations[3]["description"])
        latitude = locations[3]["latitude"]
        longitude = locations[3]["longitude"]

    else:
        output_func(f"Unknown location '{user_input}'. Defaulting to SaxaVord coordinates.")
        latitude = locations[0]["latitude"]
        longitude = locations[0]["longitude"]

    return latitude, longitude
