"""
Configurações compartilhadas para todos os testes do search_ops.
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
def file_tree(temp_dir):
    # Cria estrutura de diretórios e arquivos:
    # temp_dir/
    #   a.txt ("hello world")
    #   b.txt ("python é massa")
    #   sub/
    #     c.txt ("HELLO world\npython rules")
    sub = os.path.join(temp_dir, "sub")
    os.makedirs(sub)
    with open(os.path.join(temp_dir, "a.txt"), "w") as f:
        f.write("hello world\n")
    with open(os.path.join(temp_dir, "b.txt"), "w") as f:
        f.write("python é massa\n")
    with open(os.path.join(sub, "c.txt"), "w") as f:
        f.write("HELLO world\npython rules")
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
