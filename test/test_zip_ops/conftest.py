"""
Configurações compartilhadas para todos os testes do zip_ops.
"""
import os
import time
import tempfile
import threading
import pytest
import shutil

class DummyLogger:
    def info(self, *a, **k): pass
    def debug(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass

@pytest.fixture
def tmp_tree():
    base = tempfile.mkdtemp()
    f1 = os.path.join(base, "file1.txt")
    f2 = os.path.join(base, "file2.txt")
    with open(f1, "w") as f: f.write("abc")
    with open(f2, "w") as f: f.write("def")
    subdir = os.path.join(base, "subdir")
    os.makedirs(subdir)
    f3 = os.path.join(subdir, "file3.txt")
    with open(f3, "w") as f: f.write("ghi")
    yield base
    shutil.rmtree(base)

@pytest.fixture(autouse=True)
def dummy_progress(monkeypatch):
    # Monkeypatch ProgressPercentage para ser no-op (evita prints/lentidão)
    monkeypatch.setattr("zip_ops.ProgressPercentage", lambda *a, **k: (lambda x: None))

@pytest.fixture(autouse=True)
def dummy_logger(monkeypatch):
    monkeypatch.setattr("zip_ops.get_logger", lambda: DummyLogger())

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
