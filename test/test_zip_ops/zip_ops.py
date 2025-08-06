import os
import zipfile
from typing import List
from progress import ProgressPercentage
from logging_utils import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional


__all__ = [
    "unzip_blob_file",
    "zip_blob_file",
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


def unzip_blob_file(zip_file_path: str, destination_path: str, log: Optional[logging.Logger] = None) -> List[str]:
    """Extrai o conteúdo de um arquivo ZIP para o diretório especificado.

    Args:
        zip_file_path (str): Caminho do arquivo ZIP.
        destination_path (str): Diretório para extrair os arquivos.
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        List[str]: Lista dos arquivos extraídos.

    Raises:
        ValueError: Caso o arquivo não seja válido ou não exista.
    """
    logger = log or get_logger()
    with error_handler(f"Extracting {zip_file_path} to {destination_path}", logger):
        if not os.path.exists(zip_file_path):
            raise ValueError(f"Zip file {zip_file_path} does not exist.")

        if not zipfile.is_zipfile(zip_file_path):
            raise ValueError(f"File {zip_file_path} is not a valid zip file.")

        os.makedirs(destination_path, exist_ok=True)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                file_path = os.path.join(destination_path, file_info.filename)
                if not os.path.normpath(file_path).startswith(os.path.normpath(destination_path)):
                    raise ValueError(
                        f"Unsafe zip file: Contains path traversal attack in {file_info.filename}")

            total_files = len(zip_ref.namelist())
            processed = 0
            progress = ProgressPercentage(zip_file_path, total_files, logger)

            for member in zip_ref.infolist():
                zip_ref.extract(member, destination_path)
                processed += 1
                progress(1)

            extracted_files = zip_ref.namelist()
            logger.info(f"Extracted {len(extracted_files)} files from {zip_file_path} to {destination_path}")
            return extracted_files

def zip_blob_file(source_path: str, zip_file_path: str, compression_level: int = 9, log: Optional[logging.Logger] = None) -> str:
    """Compacta um arquivo ou diretório no formato ZIP.

    Args:
        source_path (str): Caminho do arquivo ou diretório a ser compactado.
        zip_file_path (str): Caminho do arquivo ZIP a ser criado.
        compression_level (int): Nível de compressão (0-9).
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Caminho do arquivo ZIP criado.

    Raises:
        ValueError: Caso o caminho de origem não exista.
    """
    logger = log or get_logger()
    with error_handler(f"Zipping {source_path} to {zip_file_path}", logger):
        if not os.path.exists(source_path):
            raise ValueError(f"Source path {source_path} does not exist.")

        zip_dir = os.path.dirname(zip_file_path)
        if zip_dir:
            os.makedirs(zip_dir, exist_ok=True)

        with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED,
                             compresslevel=compression_level) as zipf:
            if os.path.isdir(source_path):
                base_path = os.path.dirname(source_path)
                all_files = [os.path.join(root, f) for root, _, files in os.walk(source_path) for f in files]
                total_files = len(all_files)
                processed = 0
                progress = ProgressPercentage(source_path, total_files, logger)

                for root, _, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, base_path)
                        zipf.write(file_path, arcname)
                        processed += 1
                        progress(1)
            else:
                zipf.write(source_path, os.path.basename(source_path))

        size_bytes = os.path.getsize(zip_file_path)
        size_mb = size_bytes / (1024 * 1024)
        logger.info(f"Created zip file {zip_file_path} ({size_mb:.2f} MB)")
        return zip_file_path
