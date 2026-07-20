from pathlib import Path

# Where to save mission plot images
PLOTS_DIR = Path(__file__).with_name("plots")

# Matplotlib style name (e.g., 'seaborn', 'ggplot', 'default')
PLOT_STYLE = "seaborn"

# Whether to attempt to open the plot image after saving
# Set to False to avoid spawning external image viewers automatically.
OPEN_PLOT = False

# Maximum width for ASCII fallback bars
ASCII_MAX_WIDTH = 50
# Save separate PNGs for each metric in addition to the combined figure
SAVE_SEPARATE_PLOTS = True

# Colors for the plots (matplotlib color names)
PLOT_COLORS = {
	"fuel": "tab:blue",
	"altitude": "tab:orange",
	"accel": "tab:green",
}

# Mission log file (newline-delimited JSON). Placed in the logs folder.
MISSIONS_FILE = Path(__file__).with_name("logs") / "missions.jsonl"

# Global logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# Set to 'INFO' by default; change to 'WARNING' to suppress INFO messages.
LOG_LEVEL = "INFO"
