from locations import locations


def location_menu():
   print("\n" + "="  * 48)
   print("          LAUNCHPAD LOCATIONS")
   print("=" * 48)
   print(" 1) SaxaVord Spaceport          2) Sutherland Spaceport")
   print(" 3) Pacific Spaceport Complex   4) Mahia Launch Complex")
   print("")
   print("")


def location_choice():
   user_input = input("Please choose a number to select a launch location: ")

   choice = user_input.strip().lower()

   if choice == "1":
      print(locations[0]["description"])
      latitude = locations[0]["latitude"]
      longitude = locations[0]["longitude"]
 

   elif choice == "2":
      print(locations[1]["description"])
      latitude = locations[1]["latitude"]
      longitude = locations[1]["longitude"]
   

   elif choice == "3":
      print(")")
      print(locations[2]["description"])
      latitude = locations[2]["latitude"]
      longitude = locations[2]["longitude"]
         


   elif choice == "4":
      print(locations[3]["description"])
      latitude = locations[3]["latitude"]
      longitude = locations[3]["longitude"]
   
   else:
      print(f"Unknown location '{user_input}'. Defaulting to SaxaVord coordinates.")

   return latitude, longitude


   

 