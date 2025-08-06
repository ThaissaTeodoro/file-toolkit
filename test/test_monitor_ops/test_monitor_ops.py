import os
import time
import tempfile
import threading
import pytest

from monitor_ops import watch_file

def test_watch_file_detects_change(temp_file):
    changes = []
    stop = watch_file(temp_file, lambda f: changes.append(f), interval=0.2, max_time=2)
    # Modifica o arquivo após um pequeno delay
    time.sleep(0.3)
    with open(temp_file, "w") as f:
        f.write("mudou")
    # Aguarda um tempo para o watcher detectar
    time.sleep(0.5)
    stop.set()
    assert changes and changes[0] == temp_file

def test_watch_file_no_change(temp_file):
    changes = []
    stop = watch_file(temp_file, lambda f: changes.append(f), interval=0.2, max_time=1)
    # Não modifica arquivo
    time.sleep(1)
    stop.set()
    assert changes == []

def test_watch_file_multiple_changes(temp_file):
    changes = []
    stop = watch_file(temp_file, lambda f: changes.append(f), interval=0.1, max_time=2)
    # Modifica arquivo duas vezes
    for _ in range(2):
        time.sleep(0.2)
        with open(temp_file, "a") as f:
            f.write("x")
    time.sleep(0.4)
    stop.set()
    assert len(changes) >= 2  # Pode detectar mais vezes dependendo do SO

def test_watch_file_stops_on_stop_flag(temp_file):
    changes = []
    stop = watch_file(temp_file, lambda f: changes.append(f), interval=0.2)
    time.sleep(0.5)
    stop.set()
    time.sleep(0.5)
    # Não deve disparar callback depois de parado
    prev = len(changes)
    with open(temp_file, "a") as f:
        f.write("x")
    time.sleep(0.5)
    assert len(changes) == prev

def test_watch_file_file_not_exists():
    fake_path = "notarealfile12345.txt"
    with pytest.raises(ValueError):
        watch_file(fake_path, lambda f: None, interval=0.1, max_time=0.5)

def test_watch_file_callback_error_handling(temp_file):
    # Callback que lança exceção: watcher deve logar erro e encerrar thread
    def bad_callback(f): raise Exception("fail!")
    stop = watch_file(temp_file, bad_callback, interval=0.1, max_time=1)
    with open(temp_file, "a") as f:
        f.write("a")
    time.sleep(0.5)
    stop.set()  # Não deve travar