import unittest
from types import SimpleNamespace

from flight_computer import assess_flight_conditions


class FlightComputerTests(unittest.TestCase):
    def test_reports_low_fuel_and_warns_pilot(self):
        rocket = SimpleNamespace(fuel=10, altitude=3000)
        result = assess_flight_conditions(rocket)
        self.assertTrue(result["is_fuel_low"])
        self.assertFalse(result["is_altitude_dangerous"])
        self.assertTrue(result["should_warn_pilot"])
        self.assertTrue(result["should_shutdown_engines"])

    def test_reports_dangerous_altitude(self):
        rocket = SimpleNamespace(fuel=80, altitude=15000)
        result = assess_flight_conditions(rocket)
        self.assertFalse(result["is_fuel_low"])
        self.assertTrue(result["is_altitude_dangerous"])
        self.assertTrue(result["should_warn_pilot"])
        self.assertTrue(result["should_shutdown_engines"])

    def test_no_alerts_when_conditions_are_safe(self):
        rocket = SimpleNamespace(fuel=80, altitude=5000)
        result = assess_flight_conditions(rocket)
        self.assertFalse(result["is_fuel_low"])
        self.assertFalse(result["is_altitude_dangerous"])
        self.assertFalse(result["should_warn_pilot"])
        self.assertFalse(result["should_shutdown_engines"])


if __name__ == "__main__":
    unittest.main()
