import os
import tempfile
from typing import Optional, Union
from logging_metrics import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional

__all__ = [
    "create_temp_file",
    "create_temp_directory"
]

def get_logger() -> logging.Logger:
    """Inicializa e retorna um logger com print no console.

    Returns:
        logging.Logger: Logger basico.
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

def create_temp_file(prefix: str = "tmp_", suffix: str = "",
                     content: Optional[Union[str, bytes]] = None,
                     directory: Optional[str] = None, log: Optional[logging.Logger] = None) -> str:
    """Creates a persistent temporary file.

    Args:
        prefix (str): Filename prefix.
        suffix (str): Filename suffix.
        content (Optional[Union[str, bytes]]): Optional content to write to the file.
        directory (Optional[str]): Directory where to create the file (if None, uses the system default directory).
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        str: Path of the created temporary file.

    Raises:
        Exception: Any error creating or writing to the file.
    """
    logger = log or get_logger()
    with error_handler("Creating temporary file", logger):
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=directory)
        os.close(fd)

        if content is not None:
            if isinstance(content, str):
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with open(temp_path, 'wb') as f:
                    f.write(content)

        logger.info(f"Created temporary file: {temp_path}")
        return temp_path

def create_temp_directory(prefix: str = "tmp_",
                          base_dir: Optional[str] = None, log: Optional[logging.Logger] = None) -> str:
    """Creates a persistent temporary directory.

    Args:
        prefix (str): Directory name prefix.
        base_dir (Optional[str]): Parent directory to create (if None, uses the system default directory).
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        str: Path of the created temporary directory.

    Raises:
        Exception: Any error creating the directory.
    """
    logger = log or get_logger()

    with error_handler("Creating temporary directory", logger):
        if base_dir and not os.path.isdir(base_dir):
            os.makedirs(base_dir, exist_ok=True)

        temp_dir = tempfile.mkdtemp(prefix=prefix, dir=base_dir)
        logger.info(f"Created temporary directory: {temp_dir}")
        return temp_dir
