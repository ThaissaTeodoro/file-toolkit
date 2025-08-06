import os
import tempfile
import time
import shutil
import pytest
from search_ops import (
    list_files_blob, get_files_matching_prefix, search_file_content, get_file_modified_since
)

def test_list_files_blob_basic(file_tree):
    files = list_files_blob(file_tree)
    names = [f['name'] for f in files]
    assert set(names) == {"a.txt", "b.txt"}

def test_list_files_blob_recursive_with_dirs(file_tree):
    files = list_files_blob(file_tree, include_dirs=True, recursive=True)
    # Deve incluir subdiretório "sub" e todos arquivos
    names = [f['name'] for f in files]
    assert "sub" in names
    assert "c.txt" in names

def test_list_files_blob_error(temp_dir):
    fake_path = os.path.join(temp_dir, "not_here")
    with pytest.raises(ValueError):
        list_files_blob(fake_path)

def test_get_files_matching_prefix(file_tree):
    res = get_files_matching_prefix(file_tree, prefix="a")
    assert len(res) == 1 and res[0]['name'] == "a.txt"

def test_get_files_matching_prefix_recursive(file_tree):
    res = get_files_matching_prefix(file_tree, prefix="c", recursive=True)
    assert any(f['name'] == "c.txt" for f in res)

def test_get_files_matching_prefix_nodir(temp_dir):
    fake_path = os.path.join(temp_dir, "not_here")
    with pytest.raises(NotADirectoryError):
        get_files_matching_prefix(fake_path, prefix="x")

def test_search_file_content_basic(file_tree):
    matches = search_file_content(file_tree, "hello", file_pattern="*.txt", recursive=True)
    files = set(m['file'] for m in matches)
    assert any("a.txt" in f or "c.txt" in f for f in files)
    # Checa pelo menos 2 ocorrências ("hello" em a.txt e c.txt)
    assert len(matches) >= 2

def test_search_file_content_case_sensitive(file_tree):
    matches = search_file_content(file_tree, "HELLO", file_pattern="*.txt", recursive=True, case_sensitive=True)
    files = [m['file'] for m in matches]
    # Só c.txt tem "HELLO" em maiúsculo
    assert any("c.txt" in f for f in files)
    assert not any("a.txt" in f for f in files)

def test_search_file_content_no_match(file_tree):
    matches = search_file_content(file_tree, "nãoexiste", file_pattern="*.txt", recursive=True)
    assert matches == []

def test_get_file_modified_since(file_tree):
    # Marca arquivo como modificado agora
    a_path = os.path.join(file_tree, "a.txt")
    os.utime(a_path, None)
    res = get_file_modified_since(file_tree, days=0.01, recursive=False)
    names = [f['name'] for f in res]
    assert "a.txt" in names

def test_get_file_modified_since_recursive(file_tree):
    # Marca c.txt como modificado agora
    c_path = os.path.join(file_tree, "sub", "c.txt")
    os.utime(c_path, None)
    res = get_file_modified_since(file_tree, days=0.01, recursive=True)
    names = [f['name'] for f in res]
    assert "c.txt" in names

def test_get_file_modified_since_empty(temp_dir):
    # Diretório vazio, nada modificado
    res = get_file_modified_since(temp_dir, days=1)
    assert res == []

def test_get_file_modified_since_direrror(temp_dir):
    fake_path = os.path.join(temp_dir, "nope")
    with pytest.raises(ValueError):
        get_file_modified_since(fake_path, days=1)

def test_search_file_content_binary_file(file_tree):
    # Cria arquivo binário
    bin_path = os.path.join(file_tree, "binfile.bin")
    with open(bin_path, "wb") as f:
        f.write(b"\x00\x01\x02abc")
    matches = search_file_content(file_tree, "abc", file_pattern="*.bin", recursive=True)
    # Não deve achar nada (ignora binário)
    assert matches == []