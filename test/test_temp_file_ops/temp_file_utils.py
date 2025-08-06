import os
import tempfile
from typing import Optional, Union
from logging_utils import configure_basic_logging
import logging
from contextlib import contextmanager

__all__ = [
    "create_temp_file",
    "create_temp_directory",
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

def create_temp_file(prefix: str = "tmp_", suffix: str = "",
                     content: Optional[Union[str, bytes]] = None,
                     directory: Optional[str] = None, log: Optional[logging.Logger] = None) -> str:
    """Cria um arquivo temporário persistente.

    Args:
        prefix (str): Prefixo do nome do arquivo.
        suffix (str): Sufixo do nome do arquivo.
        content (Optional[Union[str, bytes]]): Conteúdo opcional para gravar no arquivo.
        directory (Optional[str]): Diretório onde criar o arquivo (se None, usa o diretório padrão do sistema).
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Caminho do arquivo temporário criado.

    Raises:
        Exception: Qualquer erro ao criar ou gravar no arquivo.
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
    """Cria um diretório temporário persistente.

    Args:
        prefix (str): Prefixo do nome do diretório.
        base_dir (Optional[str]): Diretório pai onde criar (se None, usa o diretório padrão do sistema).
        log (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        str: Caminho do diretório temporário criado.

    Raises:
        Exception: Qualquer erro ao criar o diretório.
    """
    logger = log or get_logger()

    with error_handler("Creating temporary directory", logger):
        if base_dir and not os.path.isdir(base_dir):
            os.makedirs(base_dir, exist_ok=True)

        temp_dir = tempfile.mkdtemp(prefix=prefix, dir=base_dir)
        logger.info(f"Created temporary directory: {temp_dir}")
        return temp_dir
