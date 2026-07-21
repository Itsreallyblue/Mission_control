#this file should only know about the rocket

import time
import random


class Rocket:
    def __init__(self, fuel=100, speed=0, altitude=0,
                 missions_completed=0, engine_temp=25, timer=0, acceleration=0, mass=500, thrust=15000):

        self.fuel = fuel
        self.speed = speed
        self.altitude = altitude
        self.missions_completed = missions_completed
        self.engine_temp = engine_temp
        self.timer = timer 
        self.acceleration = acceleration
        self.mass = mass    # Kg
        self.thrust = thrust  # Newtons of force

    def burn_fuel(self):
        fuel_loss = random.randint(5, 15)
        self.fuel = max(0, self.fuel - fuel_loss)#prevents fuel going lower than 0

    def launch(self):
        self.altitude += 1000
        self.speed += 200
        self.engine_temp += random.randint(3, 8)

    def display_status(self):
        print("\n" + "~" * 50)
        print("            ROCKET STATUS")
        print("~" * 50)
        rocket_name = getattr(self, "name", "Unnamed Rocket")
        print(f"  Rocket:         {rocket_name}")
        print(f"  Fuel:           {self.fuel:>3}%")
        print(f"  Speed:          {self.speed} m/s")
        print(f"  Altitude:       {self.altitude} m")
        print(f"  Engine Temp:    {self.engine_temp} C")
        # display mission timer in H:MM:SS when non-zero
        if getattr(self, "timer", 0):
            hrs = self.timer // 3600
            mins = (self.timer % 3600) // 60
            secs = self.timer % 60
            if hrs:
                timestr = f"{hrs}:{mins:02d}:{secs:02d}"
            else:
                timestr = f"{mins}:{secs:02d}"
            print(f"  Mission Time:   {timestr}")
        print(f"  Missions:       {self.missions_completed}")
        print("~" * 50)

    def check_engine(self):
        if self.engine_temp >= 120:
            print("⚠️ Engine overheating! Launch aborted.")
            return False
        return True


        #Notice something?
        #There's no JSON in here
        #There's no menu
        #There's no input()
        #The Rocket class only worries about being a rocket

