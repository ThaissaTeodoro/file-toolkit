import os
from typing import Dict, List, Optional
from filecmp import dircmp
import fnmatch
from progress import ProgressPercentage
from file_ops import copy_file, copy_directory, delete_path
from logging_metrics import configure_basic_logging
import logging
from contextlib import contextmanager

__all__ = [
    "sync_directories"
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

def sync_directories(source_dir: str, target_dir: str, delete: bool = False,
                     ignore_patterns: Optional[List[str]] = None, log: Optional[logging.Logger] = None) -> Dict[str, int]:
    """Synchronizes the contents of a source directory to another destination.

    Args:
        source_dir (str): Source directory.
        target_dir (str): Destination directory.
        delete (bool): Whether to delete files in the destination that do not exist in the source.
        ignore_patterns (Optional[List[str]]): File/directory patterns to ignore.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        Dict[str, int]: Statistics of the operations performed.

    Raises:
        ValueError: If the source directory does not exist.
    """
    logger = log or get_logger()
    with error_handler(f"Syncing {source_dir} to {target_dir}", logger):
        if not os.path.isdir(source_dir):
            raise ValueError(f"Source directory {source_dir} does not exist.")

        os.makedirs(target_dir, exist_ok=True)

        stats = {
            'copied': 0,
            'updated': 0,
            'deleted': 0,
            'skipped': 0
        }

        def should_ignore(path: str) -> bool:
            if not ignore_patterns:
                return False

            name = os.path.basename(path)
            return any(fnmatch.fnmatch(name, pattern) for pattern in ignore_patterns)

        def process_comparison(dcmp):
            for file in dcmp.left_only:
                src_path = os.path.join(dcmp.left, file)
                dst_path = os.path.join(dcmp.right, file)

                if should_ignore(src_path):
                    stats['skipped'] += 1
                    continue

                if os.path.isdir(src_path):
                    copy_directory(src_path, dst_path)
                    stats['copied'] += 1
                else:
                    total_size = os.path.getsize(src_path)
                    progress = ProgressPercentage(src_path, total_size, logger)
                    copy_file(src_path, os.path.dirname(dst_path), progress_callback=progress)
                    stats['copied'] += 1

            for file in dcmp.diff_files:
                src_path = os.path.join(dcmp.left, file)
                dst_path = os.path.join(dcmp.right, file)

                if should_ignore(src_path):
                    stats['skipped'] += 1
                    continue

                if os.path.isfile(src_path):
                    total_size = os.path.getsize(src_path)
                    progress = ProgressPercentage(src_path, total_size, logger)
                    copy_file(src_path, os.path.dirname(dst_path), progress_callback=progress)
                    stats['updated'] += 1

            if delete:
                for file in dcmp.right_only:
                    dst_path = os.path.join(dcmp.right, file)

                    if should_ignore(dst_path):
                        stats['skipped'] += 1
                        continue

                    delete_path(dst_path)
                    stats['deleted'] += 1

            for sub_dcmp in dcmp.subdirs.values():
                process_comparison(sub_dcmp)

        dcmp = dircmp(source_dir, target_dir)
        process_comparison(dcmp)

        logger.info(
            f"Sync completed: {stats['copied']} copied, "
            f"{stats['updated']} updated, "
            f"{stats['deleted']} deleted, "
            f"{stats['skipped']} skipped"
        )

        return stats
