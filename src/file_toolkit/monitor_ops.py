import os
import time
import threading
from typing import Optional, Callable
from logging_metrics import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional

__all__ = [
    "watch_file"
]

def get_logger() -> logging.Logger:
    """Initializes and returns a logger with a printout to the console.

    Returns:
        logging.Logger: Basic logger.
    """
    return configure_basic_logging()

@contextmanager
def error_handler(operation: str, logger: Optional[logging.Logger] = None, reraise: bool = True):
    """
    Context manager for handling errors in file operations.

    Args:
        operation: Description of the operation being performed
        logger: Logger for recording errors
        reraise: Whether to raise exceptions again after logging
    """
    try:
        yield
    except FileNotFoundError as e:
        logger.error(f"{operation} failed: File not found - {str(e)}")
        if reraise:
            raise
    except PermissionError as e:
        logger.error(f"{operation} failed: Permission denied - {str(e)}")
        if reraise:
            raise
    except Exception as e:
        logger.error(f"{operation} failed: {str(e)}")
        if reraise:
            raise

def watch_file(file_path: str, callback: Callable[[str], None], interval: float = 1.0,
               max_time: Optional[float] = None, log: Optional[logging.Logger] = None):
    """Monitors changes to a file and calls a callback when changes are detected.

    Args:
        file_path (str): Path of the file to be monitored.
        callback (Callable[[str], None]): Function called when the file changes.
        interval (float, optional): Check interval in seconds. Default is 1.0.
        max_time (Optional[float], optional): Maximum time in seconds to monitor. None for undefined.
        logger (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        threading.Event: An event object that can be used to stop monitoring.

    Raises:
        ValueError: If the file does not exist.
    """
    logger = log or get_logger()

    with error_handler(f"Setting up file watch for {file_path}", logger):
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} does not exist.")

        last_modified = os.path.getmtime(file_path)
        start_time = time.time()
        stop_flag = threading.Event()

        def watch_loop():
            nonlocal last_modified

            while not stop_flag.is_set():
                if max_time and (time.time() - start_time) > max_time:
                    logger.info(f"Reached maximum watch time for {file_path}")
                    break

                try:
                    current_modified = os.path.getmtime(file_path)
                    if current_modified != last_modified:
                        logger.debug(f"Detected change in {file_path}")
                        last_modified = current_modified
                        callback(file_path)
                except Exception as e:
                    logger.error(f"Error watching {file_path}: {str(e)}")
                    break

                time.sleep(interval)

        logger.info(f"Started watching {file_path} for changes")
        thread = threading.Thread(target=watch_loop, daemon=True)
        thread.start()

        return stop_flag
