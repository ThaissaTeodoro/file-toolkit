import os
import time
import threading
from typing import Optional, Callable
from logging_utils import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional


__all__ = [
    "watch_file",
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

def watch_file(file_path: str, callback: Callable[[str], None], interval: float = 1.0,
               max_time: Optional[float] = None, log: Optional[logging.Logger] = None):
    """Monitora alterações em um arquivo e chama um callback quando mudanças são detectadas.

    Args:
        file_path (str): Caminho do arquivo a ser monitorado.
        callback (Callable[[str], None]): Função chamada quando o arquivo muda.
        interval (float, opcional): Intervalo de checagem em segundos. Padrão 1.0.
        max_time (Optional[float], opcional): Tempo máximo em segundos para monitorar. None para indefinido.
        logger (logging.Logger, optional): Logger para auditoria. Se None, usa get_logger().

    Returns:
        threading.Event: Um objeto de evento que pode ser usado para parar a monitoração.

    Raises:
        ValueError: Caso o arquivo não exista.
    """
    logger = log or get_logger()

    with error_handler(f"Setting up file watch for {file_path}", logger):
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} does not exist.")

        last_modified = os.path.getmtime(file_path)
        start_time = time.time()
        stop_flag = threading.Event()

        def watch_loop():
            nonlocal last_modified

            while not stop_flag.is_set():
                if max_time and (time.time() - start_time) > max_time:
                    logger.info(f"Reached maximum watch time for {file_path}")
                    break

                try:
                    current_modified = os.path.getmtime(file_path)
                    if current_modified != last_modified:
                        logger.debug(f"Detected change in {file_path}")
                        last_modified = current_modified
                        callback(file_path)
                except Exception as e:
                    logger.error(f"Error watching {file_path}: {str(e)}")
                    break

                time.sleep(interval)

        logger.info(f"Started watching {file_path} for changes")
        thread = threading.Thread(target=watch_loop, daemon=True)
        thread.start()

        return stop_flag
