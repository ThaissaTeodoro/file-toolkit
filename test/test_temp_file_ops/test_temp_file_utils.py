import os
import tempfile
import shutil
import pytest
from temp_file_utils import create_temp_file, create_temp_directory

def test_create_temp_file_default():
    temp_path = create_temp_file()
    assert os.path.isfile(temp_path)
    # Limpeza
    os.remove(temp_path)

def test_create_temp_file_with_content_str():
    temp_path = create_temp_file(content="hello", suffix=".txt")
    with open(temp_path, "r", encoding="utf-8") as f:
        data = f.read()
    assert data == "hello"
    os.remove(temp_path)

def test_create_temp_file_with_content_bytes():
    temp_path = create_temp_file(content=b"\x00\x01\x02")
    with open(temp_path, "rb") as f:
        data = f.read()
    assert data == b"\x00\x01\x02"
    os.remove(temp_path)

def test_create_temp_file_in_directory():
    base_dir = tempfile.mkdtemp()
    temp_path = create_temp_file(directory=base_dir)
    assert os.path.commonpath([base_dir, temp_path]) == base_dir
    os.remove(temp_path)
    shutil.rmtree(base_dir)

def test_create_temp_file_dir_created():
    base_dir = os.path.join(tempfile.gettempdir(), "sub_dir_temp_test")
    # Garante que a pasta não existe
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    temp_path = create_temp_file(directory=base_dir)
    assert os.path.exists(base_dir)
    os.remove(temp_path)
    shutil.rmtree(base_dir)

def test_create_temp_file_with_prefix_suffix():
    temp_path = create_temp_file(prefix="mytest_", suffix=".data")
    assert os.path.basename(temp_path).startswith("mytest_")
    assert temp_path.endswith(".data")
    os.remove(temp_path)

def test_create_temp_directory_default():
    temp_dir = create_temp_directory()
    assert os.path.isdir(temp_dir)
    shutil.rmtree(temp_dir)

def test_create_temp_directory_in_base_dir():
    base_dir = tempfile.mkdtemp()
    temp_dir = create_temp_directory(base_dir=base_dir)
    assert os.path.commonpath([base_dir, temp_dir]) == base_dir
    shutil.rmtree(temp_dir)
    shutil.rmtree(base_dir)

def test_create_temp_directory_prefix():
    temp_dir = create_temp_directory(prefix="dirtest_")
    assert os.path.basename(temp_dir).startswith("dirtest_")
    shutil.rmtree(temp_dir)

def test_create_temp_directory_base_dir_created():
    base_dir = os.path.join(tempfile.gettempdir(), "custom_base_temp")
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    temp_dir = create_temp_directory(base_dir=base_dir)
    assert os.path.exists(base_dir)
    shutil.rmtree(temp_dir)
    shutil.rmtree(base_dir)
