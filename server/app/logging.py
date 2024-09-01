from datetime import datetime
from pathlib import Path
import logging

LOG_DIR = Path(__file__).parent.parent / "logs"


def setup_logger(save: bool = False):
    logger = logging.getLogger("vlm-server")
    logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    if save:
        # Create file handler
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Add file handler to logger
        logger.addHandler(file_handler)

    return logger
