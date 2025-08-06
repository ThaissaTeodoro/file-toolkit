import os
import shutil
import tempfile
import json
import pytest

from file_ops import (
    move_blob_file, move_blob_directory, copy_blob_file, delete_blob_file,
    rename_blob_file, file_exists_blob, get_bytes_by_file_path, backup_file,
    create_directory, write_text_file, read_text_file, write_binary_file,
    write_json_file, read_json_file, copy_directory, ensure_path_exists,
    order_columns_by_schema,
)

def test_create_and_write_read_text_file(temp_dir):
    file_path = os.path.join(temp_dir, "myfile.txt")
    write_text_file(file_path, "olá mundo!")
    assert os.path.isfile(file_path)
    content = read_text_file(file_path)
    assert content == "olá mundo!"

def test_write_and_read_json_file(temp_dir):
    file_path = os.path.join(temp_dir, "mydata.json")
    data = {"x": 1, "y": [1,2,3]}
    write_json_file(file_path, data)
    result = read_json_file(file_path)
    assert result == data

def test_write_and_read_binary_file(temp_dir):
    file_path = os.path.join(temp_dir, "mybin.bin")
    data = b"abc\x00\x01"
    write_binary_file(file_path, data)
    assert os.path.isfile(file_path)
    with open(file_path, "rb") as f:
        assert f.read() == data

def test_file_exists_blob(temp_file):
    assert file_exists_blob(temp_file)
    assert not file_exists_blob(temp_file + "_inex")

def test_rename_blob_file(temp_file):
    new_name = "renamed.txt"
    dir_ = os.path.dirname(temp_file)
    new_path = rename_blob_file(temp_file, new_name)
    assert os.path.isfile(new_path)
    assert not os.path.exists(temp_file)
    assert os.path.basename(new_path) == new_name

def test_move_blob_file(temp_dir, temp_file):
    dest_dir = os.path.join(temp_dir, "dest")
    os.makedirs(dest_dir)
    moved_path = move_blob_file(temp_file, dest_dir)
    assert os.path.isfile(moved_path)
    assert not os.path.exists(temp_file)

def test_copy_blob_file(temp_dir, temp_file):
    dest_dir = os.path.join(temp_dir, "copy")
    os.makedirs(dest_dir)
    copied_path = copy_blob_file(temp_file, dest_dir)
    assert os.path.isfile(copied_path)
    with open(copied_path) as f1, open(temp_file) as f2:
        assert f1.read() == f2.read()

def test_delete_blob_file(temp_file):
    assert os.path.exists(temp_file)
    deleted = delete_blob_file(temp_file)
    assert deleted is True
    assert not os.path.exists(temp_file)

def test_move_blob_directory(temp_dir):
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(src_dir)
    for fname in ("a.txt", "b.txt"):
        with open(os.path.join(src_dir, fname), "w") as f:
            f.write(fname)
    dest_dir = os.path.join(temp_dir, "dst")
    os.makedirs(dest_dir)
    move_blob_directory(src_dir, dest_dir)
    assert all(os.path.isfile(os.path.join(dest_dir, fname)) for fname in ("a.txt", "b.txt"))
    assert not os.listdir(src_dir)

def test_copy_directory(temp_dir):
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(src_dir)
    with open(os.path.join(src_dir, "a.txt"), "w") as f:
        f.write("dataa")
    dst_dir = os.path.join(temp_dir, "dst")
    copy_directory(src_dir, dst_dir)
    assert os.path.isfile(os.path.join(dst_dir, "a.txt"))

def test_backup_file(temp_file, temp_dir):
    backup_dir = os.path.join(temp_dir, "backup")
    os.makedirs(backup_dir)
    backup_path = backup_file(temp_file, backup_dir, timestamp=False)
    assert os.path.isfile(backup_path)
    with open(backup_path) as f1, open(temp_file) as f2:
        assert f1.read() == f2.read()

def test_get_bytes_by_file_path(temp_file):
    content = get_bytes_by_file_path(temp_file)
    with open(temp_file, "rb") as f:
        assert f.read() == content

def test_create_directory(temp_dir):
    path = os.path.join(temp_dir, "novo_dir")
    assert not os.path.exists(path)
    create_directory(path)
    assert os.path.isdir(path)

def test_ensure_path_exists(temp_dir):
    file_path = os.path.join(temp_dir, "folder", "my.txt")
    ensure_path_exists(file_path, is_file=True)
    assert os.path.isdir(os.path.dirname(file_path))

def test_order_columns_by_schema():
    schema = [
        {"column_name": "b", "order": 2},
        {"column_name": "a", "order": 1},
        {"column_name": "c", "order": 3}
    ]
    result = order_columns_by_schema(schema, name_column_order="order")
    assert result == ["a", "b", "c"]

# Edge cases

def test_delete_blob_file_inexistente(temp_dir):
    file_path = os.path.join(temp_dir, "nope.txt")
    # Não existe
    assert delete_blob_file(file_path) is False

def test_rename_blob_file_ja_existe(temp_file, temp_dir):
    other_path = os.path.join(temp_dir, "other.txt")
    with open(other_path, "w") as f:
        f.write("data")
    with pytest.raises(ValueError):
        rename_blob_file(temp_file, "other.txt")

def test_move_blob_directory_path_nao_existe(temp_dir):
    src_dir = os.path.join(temp_dir, "not_here")
    dest_dir = os.path.join(temp_dir, "new_dest")
    with pytest.raises(ValueError):
        move_blob_directory(src_dir, dest_dir)

def test_read_text_file_inexistente(temp_dir):
    file_path = os.path.join(temp_dir, "inexist.txt")
    with pytest.raises(FileNotFoundError):
        read_text_file(file_path)

def test_read_json_file_inexistente(temp_dir):
    file_path = os.path.join(temp_dir, "inexist.json")
    with pytest.raises(FileNotFoundError):
        read_json_file(file_path)
