import os
import shutil
from typing import Any, Dict, List, Tuple
from logging_utils import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional
from datetime import datetime
import stat

__all__ = [
    "check_disk_space",
    "get_largest_files",
    "get_directory_size",
    "find_empty_directories",
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
    Gerenciador de contexto para tratamento de erros em operações de arquivo.

    Args:
        operation: Descrição da operação que está sendo executada
        logger: Logger para registrar erros
        reraise: Se deve gerar exceções novamente após o registro
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

def _get_file_info(file_path: str, is_dir: bool = False) -> Dict[str, Any]:
        """
        Helper method to get detailed information about a file.
        
        Args:
            file_path: Path to the file
            is_dir: Whether the path is a directory
            
        Returns:
            Dictionary with file details
        """
        stats = os.stat(file_path)
        file_type = "directory" if is_dir else "file"
        
        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension[1:] if extension else ""  # Remove leading dot
        
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'type': file_type,
            'size': stats.st_size,
            'size_human': _format_size(stats.st_size),
            'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stats.st_atime).isoformat(),
            'extension': extension,
            'permissions': stat.filemode(stats.st_mode)
        }

def check_disk_space(path: str = ".", log: Optional[logging.Logger] = None) -> Tuple[int, int, int]:
    """Verifica o uso de espaço em disco para um diretório.

    Args:
        path (str): Caminho do diretório para verificar.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        Tuple[int, int, int]: Total, usado e livre em bytes.

    Raises:
        ValueError: Se o caminho não existir.
    """
    logger = log or get_logger()

    with error_handler(f"Checking disk space for {path}", logger):
        if not os.path.exists(path):
            raise ValueError(f"Path {path} does not exist.")

        total, used, free = shutil.disk_usage(path)

        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024 or unit == 'TB':
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024

        logger.info(
            f"Disk usage for {path}: "
            f"Total: {format_size(total)}, "
            f"Used: {format_size(used)} ({used/total:.1%}), "
            f"Free: {format_size(free)} ({free/total:.1%})"
        )

        return total, used, free

def get_largest_files(directory: str, count: int = 10, recursive: bool = True, log: Optional[logging.Logger] = None) -> List[Dict[str, Any]]:
    """Encontra os maiores arquivos em um diretório.

    Args:
        directory (str): Caminho do diretório.
        count (int): Quantidade de arquivos a retornar.
        recursive (bool): Busca recursiva.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        List[Dict[str, Any]]: Lista de arquivos com seus tamanhos.

    Raises:
        ValueError: Caso o diretório não exista.
    """
    logger = log or get_logger()
    with error_handler(f"Finding {count} largest files in {directory}", logger):
        if not os.path.isdir(directory):
            raise ValueError(f"Directory {directory} does not exist.")

        files = []
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    try:
                        file_size = os.path.getsize(file_path)
                        files.append((file_path, file_size))
                    except Exception as e:
                        logger.debug(f"Error getting size of {file_path}: {str(e)}")
        else:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_file():
                        try:
                            files.append((entry.path, entry.stat().st_size))
                        except Exception as e:
                            logger.debug(f"Error getting size of {entry.path}: {str(e)}")

        files.sort(key=lambda x: x[1], reverse=True)
        largest = files[:count]

        results = [_get_file_info(path) for path, _ in largest]

        logger.info(f"Found {len(results)} largest files in {directory}")
        return results

def get_directory_size(directory: str, log: Optional[logging.Logger] = None) -> int:
    """Calcula o tamanho total de um diretório.

    Args:
        directory (str): Caminho do diretório.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        int: Tamanho em bytes.

    Raises:
        ValueError: Caso o diretório não exista.
    """
    logger = log or get_logger()

    with error_handler(f"Calculating size of directory {directory}", logger):
        if not os.path.isdir(directory):
            raise ValueError(f"Directory {directory} does not exist.")

        total_size = 0
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except Exception as e:
                    logger.debug(f"Error getting size of {file_path}: {str(e)}")

        logger.info(f"Directory {directory} size: {_format_size(total_size)}")
        return total_size

def find_empty_directories(directory: str, log: Optional[logging.Logger] = None) -> List[str]:
    """Localiza diretórios vazios.

    Args:
        directory (str): Caminho do diretório.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        List[str]: Lista de caminhos de diretórios vazios.

    Raises:
        ValueError: Caso o diretório não exista.
    """
    logger = log or get_logger()

    with error_handler(f"Finding empty directories in {directory}", logger):
        if not os.path.isdir(directory):
            raise ValueError(f"Directory {directory} does not exist.")

        empty_dirs = []
        for root, dirs, files in os.walk(directory, topdown=False):
            if not files:
                is_empty = True
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if dir_path not in empty_dirs:
                        is_empty = False
                        break

                if is_empty:
                    empty_dirs.append(root)

        logger.info(f"Found {len(empty_dirs)} empty directories in {directory}")
        return empty_dirs
