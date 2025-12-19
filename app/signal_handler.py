import signal
from .shutdown import shutdown_event
from .logger import logger
import sys


def handle_shutdown(signum, frame):
    logger.info(
        "shutdown_signal_recieved",
        extra={
            "signal":signum
        }
    )
    shutdown_event.set()
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
