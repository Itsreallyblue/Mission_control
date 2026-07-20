import logging
import logging.handlers
from pathlib import Path


def setup_logging(log_dir: Path = None):
    if log_dir is None:
        log_dir = Path(__file__).with_name("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "mission_control.log"

    logger = logging.getLogger()
    if logger.handlers:
        # already configured
        return

    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file), maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # also keep console handler for convenience
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)


# auto-setup when imported
setup_logging()
