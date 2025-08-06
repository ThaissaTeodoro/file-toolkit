import os
import zipfile
import tempfile
import shutil
import pytest
import glob

from zip_ops import unzip_blob_file, zip_blob_file

def test_zip_blob_file_dir(tmp_tree):
    zip_path = os.path.join(tempfile.gettempdir(), "test_dir.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    out_zip = zip_blob_file(tmp_tree, zip_path)
    assert os.path.exists(out_zip)
    with zipfile.ZipFile(out_zip, "r") as zf:
        names = zf.namelist()
        # Deve conter todos arquivos
        assert any("file1.txt" in n for n in names)
        assert any("file2.txt" in n for n in names)
        assert any("file3.txt" in n for n in names)
    os.remove(out_zip)

def test_zip_blob_file_single_file(tmp_tree):
    file1 = os.path.join(tmp_tree, "file1.txt")
    zip_path = os.path.join(tempfile.gettempdir(), "test_file.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    out_zip = zip_blob_file(file1, zip_path)
    assert os.path.exists(out_zip)
    with zipfile.ZipFile(out_zip, "r") as zf:
        assert "file1.txt" in zf.namelist()
    os.remove(out_zip)

def test_zip_blob_file_source_not_exist():
    zip_path = os.path.join(tempfile.gettempdir(), "notexist.zip")
    with pytest.raises(ValueError):
        zip_blob_file("doesnotexist_dir_123", zip_path)


def test_unzip_blob_file_basic(tmp_tree):
    zip_path = os.path.join(tempfile.gettempdir(), "test_dir.zip")
    unzip_dir = os.path.join(tempfile.gettempdir(), "unzipped_dir")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if os.path.exists(unzip_dir):
        shutil.rmtree(unzip_dir)
    zip_blob_file(tmp_tree, zip_path)
    files = unzip_blob_file(zip_path, unzip_dir)
    matches = glob.glob(os.path.join(unzip_dir, "**", "file1.txt"), recursive=True)
    assert matches, f"'file1.txt' não encontrado em nenhum subdiretório de {unzip_dir}"
    shutil.rmtree(unzip_dir)
    os.remove(zip_path)


def test_unzip_blob_file_not_a_zip(tmp_tree):
    # Cria um arquivo .zip "fake"
    fake_zip = os.path.join(tempfile.gettempdir(), "fake.zip")
    with open(fake_zip, "w") as f:
        f.write("não é zip")
    unzip_dir = os.path.join(tempfile.gettempdir(), "fake_unzip")
    if os.path.exists(unzip_dir):
        shutil.rmtree(unzip_dir)
    with pytest.raises(ValueError):
        unzip_blob_file(fake_zip, unzip_dir)
    os.remove(fake_zip)

def test_unzip_blob_file_no_file():
    unzip_dir = os.path.join(tempfile.gettempdir(), "unzip_not_exists")
    with pytest.raises(ValueError):
        unzip_blob_file("naoexiste.zip", unzip_dir)

def test_zip_and_unzip_blob_file(tmp_tree):
    # Integração: zipa, depois descompacta, depois compara conteúdo
    zip_path = os.path.join(tempfile.gettempdir(), "test_full.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    out_zip = zip_blob_file(tmp_tree, zip_path)
    dest = tempfile.mkdtemp()
    unzip_blob_file(out_zip, dest)
    # Confere se os arquivos são os mesmos
    orig_files = set()
    for root, _, files in os.walk(tmp_tree):
        for f in files:
            orig_files.add(f)
    unzipped_files = set()
    for root, _, files in os.walk(dest):
        for f in files:
            unzipped_files.add(f)
    assert orig_files == unzipped_files
    shutil.rmtree(dest)
    os.remove(out_zip)