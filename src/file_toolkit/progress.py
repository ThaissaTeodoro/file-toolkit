from datetime import datetime
from threading import Lock
import logging
import sys

__all__ = [
    "ProgressPercentage"
]

class ProgressPercentage:
    """Displays file read/write progress as a percentage.

    Args:
        filename (str): File name or path.
        size (int): Total file size in bytes.
        logger (logging.Logger): Logger for recording progress messages.
        min_interval (float, optional): Minimum interval in seconds between updates.
    """

    def __init__(self, filename: str, size: int, logger: logging.Logger, min_interval: float = 1.0):
        self._filename = filename
        self._log = logger
        self._size = size
        self._seen_so_far = 0
        self._lock = Lock()
        self._start_time = datetime.now()
        self._last_update = datetime.now()
        self._min_interval = min_interval

    def __call__(self, bytes_amount: int):
        """Updates progress based on the number of bytes processed.

        Args:
            bytes_amount (int): Number of bytes processed since the last update.
        """
        with self._lock:
            self._seen_so_far += bytes_amount
            now = datetime.now()
            elapsed_since_last = (now - self._last_update).total_seconds()
            total_elapsed = (now - self._start_time).total_seconds()
            percentage = (self._seen_so_far / self._size) * 100 if self._size else 100
            speed = self._seen_so_far / (total_elapsed + 1e-9)

            if elapsed_since_last >= self._min_interval or self._seen_so_far == self._size:
                msg = (
                    f"\rProgresso: {self._filename} | "
                    f"{self._seen_so_far}/{self._size} bytes "
                    f"({percentage:.2f}%) | "
                    f"{speed/1024/1024:.2f} MB/s | "
                    f"{int(total_elapsed)} s decorridos"
                )
                self._log.info(msg)
                sys.stdout.write(msg)
                sys.stdout.flush()
                self._last_update = now
