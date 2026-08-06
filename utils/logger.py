import logging
import os
from datetime import datetime
from pathlib import Path

class GUILogHandler(logging.Handler):
    """Custom logging handler to route logs to a GUI text widget."""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            self.callback(msg)
        except Exception:
            self.handleError(record)

def setup_logger(gui_callback=None):
    logger = logging.getLogger("android-builder")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter("%(levelname)s:\n%(message)s\n")

    # File Handler
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    log_file = logs_dir / f"build_{timestamp}.log"
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # GUI Handler
    if gui_callback:
        gui_handler = GUILogHandler(gui_callback)
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)

    return logger

def get_logger():
    return logging.getLogger("android-builder")
