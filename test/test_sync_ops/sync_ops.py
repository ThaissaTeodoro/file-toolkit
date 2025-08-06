import os
from typing import Dict, List, Optional
from filecmp import dircmp
import fnmatch
from progress import ProgressPercentage
from file_ops import copy_blob_file, copy_directory, delete_blob_file
from logging_utils import configure_basic_logging
from typing import Dict, List, Optional
import logging
from contextlib import contextmanager

__all__ = [
    "sync_directories",
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

def sync_directories(source_dir: str, target_dir: str, delete: bool = False,
                     ignore_patterns: Optional[List[str]] = None, log: Optional[logging.Logger] = None) -> Dict[str, int]:
    """Sincroniza os conteúdos de um diretório de origem para outro destino.

    Args:
        source_dir (str): Diretório de origem.
        target_dir (str): Diretório de destino.
        delete (bool): Se deve excluir arquivos no destino que não existem na origem.
        ignore_patterns (Optional[List[str]]): Padrões de arquivos/diretórios a serem ignorados.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        Dict[str, int]: Estatísticas das operações realizadas.

    Raises:
        ValueError: Caso o diretório de origem não exista.
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
                    copy_blob_file(src_path, os.path.dirname(dst_path), progress_callback=progress)
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
                    copy_blob_file(src_path, os.path.dirname(dst_path), progress_callback=progress)
                    stats['updated'] += 1

            if delete:
                for file in dcmp.right_only:
                    dst_path = os.path.join(dcmp.right, file)

                    if should_ignore(dst_path):
                        stats['skipped'] += 1
                        continue

                    delete_blob_file(dst_path)
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
