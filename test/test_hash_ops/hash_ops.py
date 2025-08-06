import os
import hashlib
from typing import Dict, List
from logging_utils import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional

__all__ = [
    "get_file_hash",
    "find_duplicates",
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

def get_file_hash(file_path: str, algorithm: str = 'sha256', chunk_size: int = 8192, log: Optional[logging.Logger] = None) -> str:
    """Calcula o hash de um arquivo.

    Args:
        file_path (str): Caminho do arquivo.
        algorithm (str): Algoritmo de hash (ex.: 'md5', 'sha1', 'sha256').
        chunk_size (int): Tamanho do bloco de leitura.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Hash em hexadecimal.

    Raises:
        ValueError: Se o arquivo não existir.
    """
    logger = log or get_logger()

    with error_handler(f"Calculating {algorithm} hash for {file_path}", logger):
        if not os.path.isfile(file_path):
            raise ValueError(f"File {file_path} does not exist.")

        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)

        file_hash = hash_obj.hexdigest()
        logger.debug(f"{algorithm} hash for {file_path}: {file_hash}")
        return file_hash

def find_duplicates(directory: str, recursive: bool = True, log: Optional[logging.Logger] = None) -> Dict[str, List[str]]:
    """Localiza arquivos duplicados em um diretório com base no conteúdo.

    Args:
        directory (str): Caminho do diretório.
        recursive (bool): Se deve incluir subdiretórios.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        Dict[str, List[str]]: Mapeamento hash -> lista de arquivos duplicados.

    Raises:
        NotADirectoryError: Se o diretório não existir.
    """
    logger = log or get_logger()
    with error_handler(f"Finding duplicates in {directory}", logger):
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Directory {directory} does not exist.")

        hashes: Dict[str, List[str]] = {}

        def process_file(file_path):
            try:
                file_hash = get_file_hash(file_path)
                hashes.setdefault(file_hash, []).append(file_path)
            except Exception as e:
                logger.warning(f"Error processing {file_path}: {e}")

        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    process_file(os.path.join(root, file))
        else:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_file():
                        process_file(entry.path)

        duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}

        total_dupe_files = sum(len(paths) for paths in duplicates.values())
        logger.info(f"Found {len(duplicates)} sets of duplicates with {total_dupe_files} total files")

        return duplicates
