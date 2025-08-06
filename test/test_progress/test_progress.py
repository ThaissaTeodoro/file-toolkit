import logging
import io
import sys
import time
import pytest
from progress import ProgressPercentage


def test_progress_percentage_basic(dummy_logger, monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)

    size = 100
    progress = ProgressPercentage("myfile.txt", size, dummy_logger, min_interval=0)
    progress(10)
    progress(30)
    # Agora ainda não atingiu 100/100
    assert dummy_logger.messages
    last_msg = dummy_logger.messages[-1]
    assert "myfile.txt" in last_msg
    assert "100/100" not in last_msg

    # Agora completa
    progress(60)
    last_msg = dummy_logger.messages[-1]
    assert "100/100" in last_msg
    assert "(100.00%)" in last_msg

def test_progress_percentage_complete(dummy_logger, monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    size = 50
    progress = ProgressPercentage("final.txt", size, dummy_logger, min_interval=0)
    progress(20)
    progress(30)  # Chegou ao final
    assert any("50/50" in m for m in dummy_logger.messages)
    # Checa se porcentagem chega a 100%
    assert any("(100.00%)" in m for m in dummy_logger.messages)

def test_progress_percentage_exact_bytes(dummy_logger, monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    progress = ProgressPercentage("exato.txt", 30, dummy_logger, min_interval=0)
    for _ in range(3):
        progress(10)
    assert any("30/30" in m for m in dummy_logger.messages)

def test_progress_percentage_large_file(dummy_logger, monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    size = 1024 * 1024 * 100  # 100MB
    progress = ProgressPercentage("bigfile.bin", size, dummy_logger, min_interval=0)
    # Simula grandes blocos
    for _ in range(10):
        progress(1024 * 1024 * 10)
    assert any("100.00%" in m for m in dummy_logger.messages)

def test_progress_percentage_min_interval(dummy_logger, monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    size = 100
    progress = ProgressPercentage("sleep.txt", size, dummy_logger, min_interval=0.2)
    progress(20)
    progress(20)
    # Sem aguardar, não atualiza (menos que min_interval)
    msgs_before = list(dummy_logger.messages)
    time.sleep(0.25)
    progress(20)
    assert len(dummy_logger.messages) > len(msgs_before)

def test_progress_percentage_zero_size(dummy_logger, monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    progress = ProgressPercentage("empty.txt", 0, dummy_logger, min_interval=0)
    progress(1)
    assert any("(100.00%)" in m for m in dummy_logger.messages)

def test_progress_percentage_threadsafe(dummy_logger, monkeypatch):
    # Confirma que não dá erro em chamada concorrente
    import threading
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    progress = ProgressPercentage("thread.txt", 100, dummy_logger, min_interval=0)
    def worker():
        for _ in range(10):
            progress(10)
    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads: t.start()
    for t in threads: t.join()
    # Deve chegar a 100%
    assert any("100.00%" in m for m in dummy_logger.messages)

