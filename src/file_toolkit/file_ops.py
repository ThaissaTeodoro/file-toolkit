import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from progress import ProgressPercentage
from logging_metrics import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional

__all__ = [
    "move_file",
    "move_directory",
    "copy_file",
    "delete_path",
    "rename_file",
    "file_exists",
    "get_bytes_by_file_path",
    "backup_file",
    "create_directory",
    "write_text_file",
    "read_text_file",
    "write_binary_file",
    "write_json_file",
    "read_json_file",
    "copy_directory",
    "ensure_path_exists",
    "order_columns_by_schema"
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

def _format_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024 or unit == 'TB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def move_file(source_file_path: str, destination_path: str, log: Optional[logging.Logger] = None, progress_callback=None) -> str:
    """Moves a file from the source path to the destination path.

    Args:
        source_file_path (str): Source file path.
        destination_path (str): Destination directory path.
        progress_callback (Optional[callable]): Callback function for progress in bytes.

    Returns:
        str: Path of the moved file in the destination path.
    """
    destination_file_path = copy_file(source_file_path, destination_path, progress_callback)
    os.remove(source_file_path)
    logger = log or get_logger()
    logger.info(f"Moved {source_file_path} to {destination_path}")
    return destination_file_path

def move_directory(source_dir_path: str, destination_path: str, log: Optional[logging.Logger] = None) -> str:
    """Moves all contents of one directory to another.

    Args:
        source_dir_path (str): Source directory.
        destination_path (str): Destination directory.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        str: Path of the destination directory.

    Raises:
        ValueError: If source does not exist or is not a directory.
    """
    logger = log or get_logger()

    with error_handler(f"Moving directory contents {source_dir_path} to {destination_path}", logger):
        if not os.path.exists(source_dir_path):
            raise ValueError(f"Source directory {source_dir_path} does not exist.")

        if not os.path.isdir(source_dir_path):
            raise ValueError(f"Source path {source_dir_path} is not a directory.")

        os.makedirs(destination_path, exist_ok=True)

        for item in os.listdir(source_dir_path):
            source_item = os.path.join(source_dir_path, item)
            dest_item = os.path.join(destination_path, item)

            if os.path.exists(dest_item):
                if os.path.isdir(dest_item):
                    shutil.rmtree(dest_item)
                else:
                    os.remove(dest_item)

            shutil.move(source_item, dest_item)
            logger.debug(f"Moved {source_item} to {dest_item}")

        logger.info(f"Moved directory contents from {source_dir_path} to {destination_path}")
        return destination_path

def copy_file(source_file_path: str, destination_path: str, log: Optional[logging.Logger] = None, progress_callback=None) -> str:
    """Copies a file to another location.

    Args:
        source_file_path (str): Path to the source file.
        destination_path (str): Path to the destination directory.
        progress_callback (Optional[callable]): Callback function for progress in bytes.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        str: Path to the copied file in the destination.

    Raises:
        ValueError: If the source file does not exist.
    """
    logger = log or get_logger()
    with error_handler(f"Copying file {source_file_path} to {destination_path}", logger):
        if not os.path.exists(source_file_path):
            raise ValueError(f"Source file {source_file_path} does not exist.")

        os.makedirs(destination_path, exist_ok=True)
        destination_file_path = os.path.join(destination_path, os.path.basename(source_file_path))

        total_size = os.path.getsize(source_file_path)

        if progress_callback is None:
            progress_callback = ProgressPercentage(source_file_path, total_size, logger)

        buffer_size = 1024 * 1024
        with open(source_file_path, 'rb') as src, open(destination_file_path, 'wb') as dst:
            while True:
                chunk = src.read(buffer_size)
                if not chunk:
                    break
                dst.write(chunk)
                if progress_callback:
                    progress_callback(len(chunk))

        logger.info(f"Copied {source_file_path} to {destination_path}")
        return destination_file_path

def delete_path(file_path: str, log: Optional[logging.Logger] = None) -> bool:
    """Deletes a file or directory.

    Args:
        file_path (str): Path to be removed.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        bool: True if deleted, False otherwise.
    """
    logger = log or get_logger()
    with error_handler(f"Deleting {file_path}", logger, reraise=False):
        if os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file {file_path}")
            return True
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            logger.info(f"Deleted directory {file_path}")
            return True
        else:
            logger.info(f"{file_path} does not exist.")
            return False

def rename_file(source_file_path: str, new_name: str, log: Optional[logging.Logger] = None) -> str:
    """Renames a file.

    Args:
        source_file_path(str): Path of the file to rename.
        new_name(str): New name.
        log(logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        str: New file path.
    """
    logger = log or get_logger()
    with error_handler(f"Renaming {source_file_path} to {new_name}", logger):
        if not os.path.exists(source_file_path):
            raise ValueError(f"File {source_file_path} does not exist.")

        directory = os.path.dirname(source_file_path)
        new_file_path = os.path.join(directory, new_name)

        if os.path.exists(new_file_path):
            raise ValueError(f"Cannot rename: Target {new_file_path} already exists.")

        os.rename(source_file_path, new_file_path)
        logger.info(f"Renamed {source_file_path} to {new_file_path}")

        return new_file_path

def file_exists(file_path: str, log: Optional[logging.Logger] = None) -> bool:
    """Checks if a file exists.

    Args:
        file_path (str): File path.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        bool: True if exists, False otherwise.
    """
    logger = log or get_logger()
    exists = os.path.isfile(file_path)
    logger.debug(f"File exists check: {file_path} - {'Exists' if exists else 'Does not exist'}")
    return exists

def get_bytes_by_file_path(file_path: str, log: Optional[logging.Logger] = None) -> bytes:
    """Reads a file as bytes.

    Args:
        file_path (str): File path.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        bytes: File contents.
    """
    logger = log or get_logger()

    with error_handler(f"Reading file as bytes: {file_path}", logger):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, 'rb') as file:
            file_content = file.read()
            size = len(file_content)
            logger.debug(f"Read {_format_size(size)} from {file_path}")

        return file_content

def backup_file(file_path: str, backup_dir: Optional[str] = None, timestamp: bool = True, log: Optional[logging.Logger] = None) -> str:
    """Creates a backup of the file.

    Args:
        file_path (str): File path.
        backup_dir (Optional[str]): Directory to save the backup.
        timestamp (bool): Add timestamp to the name.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        str: Backup path.
    """
    logger = log or get_logger()

    with error_handler(f"Creating backup of {file_path}", logger):
        if not os.path.isfile(file_path):
            raise ValueError(f"File {file_path} does not exist.")

        if backup_dir is None:
            backup_dir = os.path.dirname(file_path) or '.'

        os.makedirs(backup_dir, exist_ok=True)

        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)

        if timestamp:
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{name}_backup_{timestamp_str}{ext}"
        else:
            backup_name = f"{name}_backup{ext}"

        backup_path = os.path.join(backup_dir, backup_name)

        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

        return backup_path

def create_directory(directory_path: str, mode: int = 0o755, log: Optional[logging.Logger] = None) -> str:
    """Creates a directory if it doesn't exist.

    Args:
        directory_path (str): Directory path.
        mode (int): Directory permissions.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        str: Directory path.
    """
    logger = log or get_logger()

    with error_handler(f"Creating directory {directory_path}", logger):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, mode=mode, exist_ok=True)
            logger.info(f"Created directory {directory_path}")
        else:
            logger.debug(f"Directory {directory_path} already exists")

        return directory_path

def write_text_file(file_path: str, content: str, encoding: str = 'utf-8', backup: bool = False, log: Optional[logging.Logger] = None) -> str:
    """Writes text content to a file.

    Args:
        file_path (str): Path to the text file.
        content (str): Text content to write.
        encoding (str, optional): File encoding. Defaults to 'utf-8'.
        backup (bool, optional): Whether to create a backup if the file already exists. Defaults to False.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        str: Path to the written file.
    """
    logger = log or get_logger()

    with error_handler(f"Writing to text file {file_path}", logger):
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if backup and os.path.exists(file_path):
            backup_file(file_path)

        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)

        logger.info(f"Wrote {len(content)} characters to {file_path}")
        return file_path

def read_text_file(file_path: str, encoding: str = 'utf-8', log: Optional[logging.Logger] = None) -> str:
    """Reads the content of a text file.

    Args:
        file_path (str): Path to the text file.
        encoding (str, optional): File encoding. Defaults to 'utf-8'.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        str: Content of the file.
    
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    logger = log or get_logger()

    with error_handler(f"Reading text file {file_path}", logger):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()

        logger.debug(f"Read {len(content)} characters from {file_path}")
        return content

def write_binary_file(file_path: str, data: bytes, backup: bool = False, log: Optional[logging.Logger] = None) -> str:
    """Writes binary data to a file.

    Args:
        file_path (str): Path to the binary file.
        data (bytes): Binary data to write.
        backup (bool, optional): Whether to create a backup if the file already exists. Defaults to False.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        str: Path to the written file.
    """
    logger = log or get_logger()
    
    with error_handler(f"Writing binary data to {file_path}", logger):
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if backup and os.path.exists(file_path):
            backup_file(file_path)

        with open(file_path, 'wb') as f:
            f.write(data)

        size = len(data)
        logger.info(f"Wrote {_format_size(size)} of binary data to {file_path}")
        return file_path

def write_json_file(file_path: str, data: Any, indent: int = 4, sort_keys: bool = False, backup: bool = False, log: Optional[logging.Logger] = None) -> str:
    """Writes JSON data to a file.

    Args:
        file_path (str): Path to the output JSON file.
        data (Any): Data to be serialized as JSON.
        indent (int, optional): Number of spaces for indentation. Defaults to 4.
        sort_keys (bool, optional): Whether to sort dictionary keys. Defaults to False.
        backup (bool, optional): Whether to create a backup if the file already exists. Defaults to False.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        str: Path to the written file.
    """
    logger = log or get_logger()

    with error_handler(f"Writing JSON to {file_path}", logger):
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if backup and os.path.exists(file_path):
            backup_file(file_path)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, sort_keys=sort_keys)

        logger.info(f"Wrote JSON data to {file_path}")
        return file_path

def read_json_file(file_path: str, log: Optional[logging.Logger] = None) -> Any:
    """Reads and parses a JSON file.

    Args:
        file_path (str): Path to the JSON file.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        Any: Parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    logger = log or get_logger()

    with error_handler(f"Reading JSON from {file_path}", logger):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.debug(f"Read and parsed JSON from {file_path}")
        return data

def copy_directory(source_dir: str, destination_dir: str, symlinks: bool = False, ignore_patterns: Optional[List[str]] = None, log: Optional[logging.Logger] = None) -> str:
    """Copies a directory and all its contents to a new location.

    Args:
        source_dir (str): Path to the source directory.
        destination_dir (str): Path to the destination directory.
        symlinks (bool, optional): Whether to copy symbolic links as links. Defaults to False.
        ignore_patterns (Optional[List[str]], optional): List of glob patterns to ignore. Defaults to None.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        str: Path to the destination directory.

    Raises:
        ValueError: If the source directory does not exist.7777                                 Q
    """
    logger = log or get_logger()

    with error_handler(f"Copying directory {source_dir} to {destination_dir}", logger):
        if not os.path.isdir(source_dir):
            raise ValueError(f"Source directory {source_dir} does not exist.")

        if os.path.exists(destination_dir):
            logger.warning(f"Destination {destination_dir} already exists, files may be overwritten")

        ignore_func = None
        if ignore_patterns:
            def ignore_func(src, names):
                ignored = set()
                for pattern in ignore_patterns:
                    import fnmatch
                    ignored.update(fnmatch.filter(names, pattern))
                return ignored

        os.makedirs(destination_dir, exist_ok=True)

        for item in os.listdir(source_dir):
            src_item = os.path.join(source_dir, item)
            dst_item = os.path.join(destination_dir, item)

            if ignore_func and item in ignore_func(source_dir, os.listdir(source_dir)):
                continue

            if os.path.isdir(src_item):
                if not os.path.exists(dst_item):
                    os.makedirs(dst_item)
                copy_directory(src_item, dst_item, symlinks, ignore_patterns)
            else:
                if symlinks and os.path.islink(src_item):
                    linkto = os.readlink(src_item)
                    os.symlink(linkto, dst_item)
                else:
                    shutil.copy2(src_item, dst_item)

        logger.info(f"Copied directory {source_dir} to {destination_dir}")
        return destination_dir

def ensure_path_exists(path: str, is_file: bool = False, log: Optional[logging.Logger] = None) -> str:
    """Ensures that the given path exists.

    Args:
        path (str): File or directory path to ensure.
        is_file (bool, optional): If True, ensures the parent directory exists (for file paths). Defaults to False.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        str: The validated or created path.
    """
    logger = log or get_logger()

    with error_handler(f"Ensuring path exists: {path}", logger):
        if is_file:
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Created directory structure for file: {path}")
        else:
            os.makedirs(path, exist_ok=True)
            logger.debug(f"Created directory: {path}")

        return path

def order_columns_by_schema(schema: List[Dict], name_column_order: str, name_column: str = 'column_name', log: Optional[logging.Logger] = None) -> List[str]:
    """Orders column names based on schema metadata.

    Args:
        schema (List[Dict]): Schema metadata, where each item is a dictionary.
        name_column_order (str): Key in the schema dict used for sorting.
        name_column (str, optional): Key in the schema dict containing the column name. Defaults to 'column_name'.
        log (Optional[logging.Logger], optional): Logger for auditing. If None, a default logger is used.

    Returns:
        List[str]: Ordered list of column names.

    Raises:
        KeyError: If required keys are missing in any schema item.
    """
    logger = log or get_logger()

    with error_handler(f"Ordering columns by {name_column_order}", logger):
        if not schema:
            logger.warning("Empty schema provided for ordering")
            return []

        if not all(name_column_order in item and name_column in item for item in schema):
            missing = [i for i, item in enumerate(schema) if name_column_order not in item or name_column not in item]
            raise KeyError(f"Schema items at indices {missing} are missing required keys")

        ordered_list = sorted(schema, key=lambda d: d[name_column_order])

        ordered_columns = [item[name_column] for item in ordered_list]
        logger.debug(f"Ordered {len(ordered_columns)} columns")

        return ordered_columns
