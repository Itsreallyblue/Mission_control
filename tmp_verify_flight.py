import sys
sys.path.insert(0, 'd:/Mission_control')
from rocket import Rocket
from flight_computer import assess_flight_conditions

rocket = Rocket(fuel=15, altitude=11000)
print(assess_flight_conditions(rocket))
