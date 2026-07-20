import logging
import logging.handlers
from pathlib import Path
import json

try:
    import settings
except Exception:
    settings = None


def setup_logging(log_dir: Path = None):
    if log_dir is None:
        log_dir = Path(__file__).with_name("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "mission_control.log"

    logger = logging.getLogger()
    if logger.handlers:
        # already configured
        return

    # derive level from settings.LOG_LEVEL if present
    level_name = getattr(settings, "LOG_LEVEL", "INFO") if settings is not None else "INFO"
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file), maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.name = "file"
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # also keep console handler for convenience
    ch = logging.StreamHandler()
    ch.name = "console"
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # reduce noise from third-party libraries (matplotlib font probing etc.)
    try:
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
    except Exception:
        pass


# auto-setup when imported
setup_logging()


def set_log_level(level_name: str):
    """Set the root logger level at runtime (e.g. 'DEBUG', 'INFO')."""
    logger = logging.getLogger()
    level = getattr(logging, level_name.upper(), None)
    if level is None:
        raise ValueError(f"Unknown log level: {level_name}")
    logger.setLevel(level)
    # persist
    try:
        _write_prefs(log_level=level_name.upper())
    except Exception:
        pass


def get_log_level() -> str:
    logger = logging.getLogger()
    return logging.getLevelName(logger.level)


def is_console_enabled() -> bool:
    logger = logging.getLogger()
    for h in logger.handlers:
        if getattr(h, "name", None) == "console":
            return True
    return False


def set_console_enabled(enabled: bool):
    logger = logging.getLogger()
    # find console handler
    console_handler = None
    for h in list(logger.handlers):
        if getattr(h, "name", None) == "console":
            console_handler = h
            break
    if enabled and console_handler is None:
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        ch = logging.StreamHandler()
        ch.name = "console"
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    if not enabled and console_handler is not None:
        logger.removeHandler(console_handler)
    # persist
    try:
        _write_prefs(console_enabled=enabled)
    except Exception:
        pass


# persistent settings file for logger preferences
def _settings_file(log_dir: Path = None) -> Path:
    if log_dir is None:
        log_dir = Path(__file__).with_name("logs")
    return log_dir / "logger_settings.json"


def _write_prefs(log_level: str = None, console_enabled: bool = None):
    sf = _settings_file()
    prefs = {}
    if sf.exists():
        try:
            prefs = json.loads(sf.read_text(encoding="utf-8"))
        except Exception:
            prefs = {}
    if log_level is not None:
        prefs["log_level"] = log_level
    if console_enabled is not None:
        prefs["console_enabled"] = bool(console_enabled)
    try:
        sf.parent.mkdir(parents=True, exist_ok=True)
        sf.write_text(json.dumps(prefs), encoding="utf-8")
    except Exception:
        pass


def _read_prefs() -> dict:
    sf = _settings_file()
    if not sf.exists():
        return {}
    try:
        return json.loads(sf.read_text(encoding="utf-8"))
    except Exception:
        return {}


# apply persisted prefs at startup
_prefs = _read_prefs()
if _prefs:
    lvl = _prefs.get("log_level")
    if lvl:
        try:
            set_log_level(lvl)
        except Exception:
            pass
    ce = _prefs.get("console_enabled")
    if ce is not None:
        try:
            set_console_enabled(bool(ce))
        except Exception:
            pass


def get_log_file_path() -> Path:
    """Return the path to the main log file."""
    return Path(__file__).with_name("logs") / "mission_control.log"


def write_plain_log(message: str):
    """Append a plain message to the main log file without logger formatting.

    This writes the message exactly as provided, followed by a newline.
    Use for user-facing telemetry and mission-summary lines where timestamps
    and level prefixes are undesired.
    """
    try:
        sf = get_log_file_path()
        sf.parent.mkdir(parents=True, exist_ok=True)
        with sf.open("a", encoding="utf-8") as f:
            f.write(str(message) + "\n")
    except Exception:
        # best-effort only; do not raise
        pass
