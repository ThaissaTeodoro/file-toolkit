import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from progress import ProgressPercentage
from logging_utils import configure_basic_logging
import logging
from contextlib import contextmanager


__all__ = [
    "move_blob_file",
    "move_blob_directory",
    "copy_blob_file",
    "delete_blob_file",
    "rename_blob_file",
    "file_exists_blob",
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
    "order_columns_by_schema",
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

def move_blob_file(source_file_path: str, destination_path: str, log: Optional[logging.Logger] = None, progress_callback=None) -> str:
    """Move um arquivo do caminho de origem para o destino.

    Args:
        source_file_path (str): Caminho do arquivo de origem.
        destination_path (str): Caminho do diretório de destino.
        progress_callback (Optional[callable]): Função callback para progresso em bytes.

    Returns:
        str: Caminho do arquivo movido no destino.
    """
    destination_file_path = copy_blob_file(source_file_path, destination_path, progress_callback)
    os.remove(source_file_path)
    logger = log or get_logger()
    logger.info(f"Moved {source_file_path} to {destination_path}")
    return destination_file_path

def move_blob_directory(source_dir_path: str, destination_path: str, log: Optional[logging.Logger] = None) -> str:
    """Move todo o conteúdo de um diretório para outro.

    Args:
        source_dir_path (str): Diretório de origem.
        destination_path (str): Diretório de destino.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Caminho do diretório de destino.

    Raises:
        ValueError: Se a origem não existir ou não for um diretório.
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

def copy_blob_file(source_file_path: str, destination_path: str, log: Optional[logging.Logger] = None, progress_callback=None) -> str:
    """Copia um arquivo para outro local.

    Args:
        source_file_path (str): Caminho do arquivo de origem.
        destination_path (str): Caminho do diretório de destino.
        progress_callback (Optional[callable]): Função callback para progresso em bytes.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Caminho do arquivo copiado no destino.

    Raises:
        ValueError: Se o arquivo de origem não existir.
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

def delete_blob_file(file_path: str, log: Optional[logging.Logger] = None) -> bool:
    """Deleta um arquivo ou diretório.

    Args:
        file_path (str): Caminho a ser removido.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        bool: True se deletado, False caso contrário.
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

def rename_blob_file(source_file_path: str, new_name: str, log: Optional[logging.Logger] = None) -> str:
    """Renomeia um arquivo.

    Args:
        source_file_path (str): Caminho do arquivo a renomear.
        new_name (str): Novo nome.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Novo caminho do arquivo.
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

def file_exists_blob(file_path: str, log: Optional[logging.Logger] = None) -> bool:
    """Verifica se um arquivo existe.

    Args:
        file_path (str): Caminho do arquivo.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        bool: True se existir, False caso contrário.
    """
    logger = log or get_logger()
    exists = os.path.isfile(file_path)
    logger.debug(f"File exists check: {file_path} - {'Exists' if exists else 'Does not exist'}")
    return exists

def get_bytes_by_file_path(file_path: str, log: Optional[logging.Logger] = None) -> bytes:
    """Lê um arquivo como bytes.

    Args:
        file_path (str): Caminho do arquivo.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        bytes: Conteúdo do arquivo.
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
    """Cria um backup do arquivo.

    Args:
        file_path (str): Caminho do arquivo.
        backup_dir (Optional[str]): Diretório para salvar backup.
        timestamp (bool): Adicionar timestamp ao nome.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Caminho do backup.
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
    """Cria um diretório caso não exista.

    Args:
        directory_path (str): Caminho do diretório.
        mode (int): Permissões do diretório.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Caminho do diretório.
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
    """Escreve texto em arquivo."""
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
    """Lê o conteúdo de um arquivo texto."""
    logger = log or get_logger()

    with error_handler(f"Reading text file {file_path}", logger):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()

        logger.debug(f"Read {len(content)} characters from {file_path}")
        return content

def write_binary_file(file_path: str, data: bytes, backup: bool = False, log: Optional[logging.Logger] = None) -> str:
    """Escreve dados binários em arquivo."""
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
    """Escreve um JSON em arquivo."""
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
    """Lê um arquivo JSON."""
    logger = log or get_logger()

    with error_handler(f"Reading JSON from {file_path}", logger):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.debug(f"Read and parsed JSON from {file_path}")
        return data

def copy_directory(source_dir: str, destination_dir: str, symlinks: bool = False, ignore_patterns: Optional[List[str]] = None, log: Optional[logging.Logger] = None) -> str:
    """Copia um diretório e todo seu conteúdo."""
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
    """Garante que um caminho existe."""
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
    """Ordena colunas de acordo com metadados do schema."""
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
