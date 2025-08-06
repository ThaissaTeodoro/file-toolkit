import os
import tempfile
import pytest
from sync_ops import sync_directories
import shutil

def create_file(path, content=b"content"):
    with open(path, "wb") as f:
        f.write(content)

def test_sync_basic_copy(src_and_dst_dirs, monkeypatch):
    src, dst = src_and_dst_dirs
    # Cria arquivos em src
    create_file(os.path.join(src, "a.txt"), b"A"*10)
    os.mkdir(os.path.join(src, "folder"))
    create_file(os.path.join(src, "folder", "b.txt"), b"B"*20)

    # Mocks para file_ops (opcional)
    monkeypatch.setattr("progress.ProgressPercentage", lambda f,s,l: (lambda n: None))
    monkeypatch.setattr("file_ops.copy_blob_file", shutil.copy)
    monkeypatch.setattr("file_ops.copy_directory", shutil.copytree)
    monkeypatch.setattr("file_ops.delete_blob_file", lambda p: os.remove(p) if os.path.isfile(p) else shutil.rmtree(p))

    stats = sync_directories(src, dst)
    # Todos arquivos devem ser copiados (2 arquivos, 1 pasta)
    assert stats["copied"] >= 2
    assert os.path.exists(os.path.join(dst, "a.txt"))
    assert os.path.exists(os.path.join(dst, "folder", "b.txt"))

def test_sync_update_files(src_and_dst_dirs, monkeypatch):
    src, dst = src_and_dst_dirs
    f1 = os.path.join(src, "a.txt")
    f2 = os.path.join(dst, "a.txt")
    create_file(f1, b"old")
    os.makedirs(os.path.dirname(f2), exist_ok=True)
    create_file(f2, b"different")  # arquivo diferente no destino

    monkeypatch.setattr("progress.ProgressPercentage", lambda f,s,l: (lambda n: None))
    monkeypatch.setattr("file_ops.copy_blob_file", shutil.copy)

    stats = sync_directories(src, dst)
    assert stats["updated"] >= 1 or stats["copied"] >= 1

def test_sync_delete_enabled(src_and_dst_dirs, monkeypatch):
    src, dst = src_and_dst_dirs
    create_file(os.path.join(src, "keep.txt"), b"data")
    create_file(os.path.join(dst, "keep.txt"), b"data")
    create_file(os.path.join(dst, "remove.txt"), b"remove_me")

    monkeypatch.setattr("progress.ProgressPercentage", lambda f,s,l: (lambda n: None))
    monkeypatch.setattr("file_ops.copy_blob_file", shutil.copy)
    monkeypatch.setattr("file_ops.delete_blob_file", lambda p: os.remove(p) if os.path.isfile(p) else shutil.rmtree(p))

    stats = sync_directories(src, dst, delete=True)
    assert stats["deleted"] == 1
    assert not os.path.exists(os.path.join(dst, "remove.txt"))
    assert os.path.exists(os.path.join(dst, "keep.txt"))

def test_sync_ignore_patterns(src_and_dst_dirs, monkeypatch):
    src, dst = src_and_dst_dirs
    create_file(os.path.join(src, "a.log"), b"log")
    create_file(os.path.join(src, "b.txt"), b"data")
    monkeypatch.setattr("progress.ProgressPercentage", lambda f,s,l: (lambda n: None))
    monkeypatch.setattr("file_ops.copy_blob_file", shutil.copy)

    stats = sync_directories(src, dst, ignore_patterns=["*.log"])
    # b.txt deve ser copiado, a.log ignorado (skipped)
    assert stats["skipped"] == 1
    assert os.path.exists(os.path.join(dst, "b.txt"))
    assert not os.path.exists(os.path.join(dst, "a.log"))

def test_sync_dir_nao_existe(monkeypatch):
    fake_src = "nao_existe_abc"
    dst = tempfile.mkdtemp()
    monkeypatch.setattr("progress.ProgressPercentage", lambda f,s,l: (lambda n: None))
    with pytest.raises(ValueError):
        sync_directories(fake_src, dst)
    shutil.rmtree(dst)
