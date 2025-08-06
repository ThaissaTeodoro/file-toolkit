import os
import tempfile
import shutil
import pytest
from stats_ops import (
    check_disk_space, get_largest_files, get_directory_size, find_empty_directories
)

def test_check_disk_space_basic(temp_dir):
    total, used, free = check_disk_space(temp_dir)
    assert total > 0 and free > 0 and used >= 0

def test_check_disk_space_path_nao_existe():
    with pytest.raises(ValueError):
        check_disk_space("not_a_real_dir_abcde12345")

def test_get_largest_files_basic(tree_for_stats):
    largest = get_largest_files(tree_for_stats, count=2)
    sizes = [f['size'] for f in largest]
    names = [f['name'] for f in largest]
    assert "file2.txt" in names
    assert "file3.txt" in names or "file1.txt" in names
    assert sizes[0] >= sizes[1]

def test_get_largest_files_non_recursive(tree_for_stats):
    res = get_largest_files(tree_for_stats, count=10, recursive=False)
    # Só deve encontrar file1.txt e file2.txt (não desce no sub)
    names = [f['name'] for f in res]
    assert set(names) == {"file1.txt", "file2.txt"}

def test_get_largest_files_dir_nao_existe():
    with pytest.raises(ValueError):
        get_largest_files("naoexiste123", count=2)

def test_get_directory_size(tree_for_stats):
    # Deve ser a soma dos tamanhos dos arquivos (100+300+200)
    total_size = get_directory_size(tree_for_stats)
    assert 590 < total_size < 700  # Considerando algum overhead possível

def test_get_directory_size_vazio(temp_dir):
    # Diretório vazio deve ter size 0
    assert get_directory_size(temp_dir) == 0

def test_get_directory_size_dir_nao_existe():
    with pytest.raises(ValueError):
        get_directory_size("naoexiste123")

def test_find_empty_directories(tree_for_stats):
    empties = find_empty_directories(tree_for_stats)
    # Deve conter pelo menos a pasta "empty"
    assert any("empty" in d for d in empties)

def test_find_empty_directories_dir_nao_existe():
    with pytest.raises(ValueError):
        find_empty_directories("fake_folder_abc")

def test_find_empty_directories_nao_vazio(temp_dir):
    # Cria um arquivo dentro de temp_dir
    with open(os.path.join(temp_dir, "foo.txt"), "w") as f:
        f.write("bar")
    # Agora temp_dir não é vazio
    empties = find_empty_directories(temp_dir)
    assert temp_dir not in empties