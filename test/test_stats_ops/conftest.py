"""
Configurações compartilhadas para todos os testes do stats_ops.
"""

import os
import time
import tempfile
import threading
import pytest
import shutil

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

@pytest.fixture
def tree_for_stats(temp_dir):
    # Estrutura:
    # temp_dir/
    #   file1.txt (100 bytes)
    #   file2.txt (300 bytes)
    #   sub/
    #     file3.txt (200 bytes)
    #   empty/
    sub = os.path.join(temp_dir, "sub")
    empty = os.path.join(temp_dir, "empty")
    os.makedirs(sub)
    os.makedirs(empty)
    f1 = os.path.join(temp_dir, "file1.txt")
    f2 = os.path.join(temp_dir, "file2.txt")
    f3 = os.path.join(sub, "file3.txt")
    with open(f1, "wb") as f: f.write(b"a" * 100)
    with open(f2, "wb") as f: f.write(b"b" * 300)
    with open(f3, "wb") as f: f.write(b"c" * 200)
    return temp_dir

# Mock logger
class MockLogger:
    """Logger simulado para testes que não precisam de logging real."""
    def __init__(self):
        self.debug_calls, self.info_calls, self.warning_calls, self.error_calls = [], [], [], []
    def debug(self, msg): self.debug_calls.append(msg)
    def info(self, msg): self.info_calls.append(msg)
    def warning(self, msg): self.warning_calls.append(msg)
    def error(self, msg): self.error_calls.append(msg)

@pytest.fixture
def mock_logger():
    """Fixture que fornece um mock logger."""
    return MockLogger()

def pytest_collection_modifyitems(config, items):
    """
    Marca testes automaticamente conforme uso de fixtures ou nome.
    """
    for item in items:
        # Marca testes que usam SparkSession
        if "spark" in item.fixturenames:
            item.add_marker(pytest.mark.spark)
        # Marca performance, integração ou stress por nome ou classe
        if "Performance" in item.nodeid or "large" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "Integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "Stress" in item.nodeid:
            item.add_marker(pytest.mark.stress)
        # Marca unit por padrão
        if "Test" in item.nodeid and all(x not in item.nodeid for x in ["Performance", "Integration", "Stress"]):
            item.add_marker(pytest.mark.unit)
        # Marca slow se nome indicar
        if any(keyword in item.name.lower() for keyword in ["large", "performance", "slow"]):
            item.add_marker(pytest.mark.slow)
