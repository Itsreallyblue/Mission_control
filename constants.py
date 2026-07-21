from pathlib import Path

# Plotting and logging settings
PLOTS_DIR = Path(__file__).with_name("plots")
PLOT_STYLE = "seaborn"
OPEN_PLOT = True
ASCII_MAX_WIDTH = 50
SAVE_SEPARATE_PLOTS = True
PLOT_COLORS = {
    "fuel": "tab:blue",
    "altitude": "tab:orange",
    "accel": "tab:green",
}
MISSIONS_FILE = Path(__file__).with_name("logs") / "missions.jsonl"
LOG_LEVEL = "INFO"

# Mission and launch dynamics
LAUNCH_COUNTDOWN_SECONDS = 5
LAUNCH_MIN_DURATION = 8
LAUNCH_MAX_DURATION = 16
FUEL_LOW_THRESHOLD = 20
ALTITUDE_DANGER_THRESHOLD = 10000
ENGINE_OVERHEAT_THRESHOLD_C = 900.0
ENGINE_HEAT_RATE_PER_THROTTLE = 0.03
ESCAPE_ALTITUDE_M = 10000
ESCAPE_VELOCITY_BASE_M_PER_S = 11186.0
DRAG_COEFFICIENT = 0.08
