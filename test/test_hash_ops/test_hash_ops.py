import os
import tempfile
import shutil
import pytest
from hash_ops import get_file_hash, find_duplicates

def test_get_file_hash_basic(temp_file):
    h = get_file_hash(temp_file)
    assert isinstance(h, str)
    # Verifica que calcular novamente retorna o mesmo hash
    h2 = get_file_hash(temp_file)
    assert h == h2

def test_get_file_hash_md5(temp_file):
    h = get_file_hash(temp_file, algorithm="md5")
    assert len(h) == 32

def test_get_file_hash_nonexistent(temp_dir):
    file_path = os.path.join(temp_dir, "nope.txt")
    with pytest.raises(ValueError):
        get_file_hash(file_path)

def test_find_duplicates_none(temp_dir):
    # Cria dois arquivos diferentes
    with open(os.path.join(temp_dir, "a.txt"), "w") as f:
        f.write("data")
    with open(os.path.join(temp_dir, "b.txt"), "w") as f:
        f.write("other")
    result = find_duplicates(temp_dir)
    assert result == {}

def test_find_duplicates_some(temp_dir):
    # Cria dois arquivos iguais e um diferente
    file_a = os.path.join(temp_dir, "a.txt")
    file_b = os.path.join(temp_dir, "b.txt")
    file_c = os.path.join(temp_dir, "c.txt")
    for f in [file_a, file_b]:
        with open(f, "w") as fobj:
            fobj.write("data")
    with open(file_c, "w") as fobj:
        fobj.write("different")
    result = find_duplicates(temp_dir)
    # Deve haver 1 hash com dois arquivos
    dupe_hashes = [h for h, files in result.items() if len(files) == 2]
    assert len(dupe_hashes) == 1
    files = result[dupe_hashes[0]]
    assert set(files) == {file_a, file_b}

def test_find_duplicates_recursive(temp_dir):
    # Cria arquivos iguais em subdiretórios
    sub = os.path.join(temp_dir, "sub")
    os.makedirs(sub)
    file1 = os.path.join(temp_dir, "a.txt")
    file2 = os.path.join(sub, "a.txt")
    with open(file1, "w") as f: f.write("xxx")
    with open(file2, "w") as f: f.write("xxx")
    result = find_duplicates(temp_dir, recursive=True)
    found = False
    for files in result.values():
        if set(files) == {file1, file2}:
            found = True
    assert found

def test_find_duplicates_notadir(temp_dir):
    fake_path = os.path.join(temp_dir, "nope_dir")
    with pytest.raises(NotADirectoryError):
        find_duplicates(fake_path)

# Edge: arquivo vazio
def test_get_file_hash_empty(temp_dir):
    file_path = os.path.join(temp_dir, "empty.txt")
    with open(file_path, "w"):
        pass
    h = get_file_hash(file_path)
    assert isinstance(h, str)
    assert len(h) > 0

def test_find_duplicates_empty_dir(temp_dir):
    result = find_duplicates(temp_dir)
    assert result == {}
