
# file-toolkit - File Operations & Utilities for Python

A robust utility library for managing files, directories, synchronization, compression, monitoring, hashing, and temporary operations—ideal for data pipelines, ETL jobs, and audit-ready file processing workflows.

---
## Features

- 🗂️ File and directory operations (copy, move, delete, backup, etc.)
- 📦 ZIP compression and extraction with progress tracking
- 🔄 Directory synchronization with conflict resolution
- 🔍 Content and metadata search utilities
- 🧾 JSON, text, and binary file read/write with logging
- 🔐 File hashing and duplicate detection
- 📈 Disk usage, file size stats, and empty directory checks
- 📡 File monitoring with callback support
- 🧪 Temporary file and directory creation
- 🧾 Built-in progress percentage logger for large files

---

## 📦 Installation

#### Install via pip:
```bash
pip install file-toolkit 
```

#### For development:
```bash
git clone https://github.com/ThaissaTeodoro/file-toolkit.git
cd file-toolkit
pip install -e ".[dev]"
```

---
## 📋 Main Modules Overview

```
| Module                  | Description                                                                          |
|-------------------------|--------------------------------------------------------------------------------------|
| `file_ops`              | Safe operations: copy, move, delete, rename, backup, read/write.                     |
| `zip_ops`               | Compress and extract files/directories (with validation & progress).                 |
| `hash_ops`              | Generate file hashes and find duplicates.                                            |
| `search_ops`            | List, filter and search files by name, content, time or prefix.                      |
| `stats_ops`             | Disk usage, directory size, and file statistics.                                     |
| `sync_ops`              | Sync directories with copy/update/delete logic and ignore rules.                     |
| `monitor_ops`           | Watch file changes and trigger callbacks.                                            |
| `temp_file_utils`       | Create temporary files and directories.                                              |
| `progress`              | Log download/upload progress for large files.                                        |
```
---

## 🚀 Quick Start

```python
from file_toolkit import move_file, unzip_file, ProgressPercentage

# Move a file to a destination
move_file("source.csv", "/tmp/")

# Extract a zip file
unzip_file("data.zip", "extracted/")

# Custom progress tracking for large file copy
from file_toolkit import copy_file
progress = ProgressPercentage("bigfile.zip", 1024*1024*500, logger)
copy_file("bigfile.zip", "/dest/", progress_callback=progress)
```

---

## 🧩 Key Utilities by Category

1. File Operations (file_ops):
    ```python
    from file_toolkit import write_text_file, read_json_file, backup_file

    write_text_file("config.txt", "content here")
    data = read_json_file("settings.json")
    backup = backup_file("data.csv")
    ```

2. Compression (zip_ops):
    ```python
    from file_toolkit import zip_file, unzip_file

    # Create zip
    zip_file("folder/", "backup.zip")

    # Extract zip
    unzip_file("backup.zip", "output/")  
    )
    ```

3. Search & Metadata (search_ops):
    ```python
    from file_toolkit import list_dir_contents, search_file_content

    files = list_dir_contents("./data", recursive=True)
    matches = search_file_content("./logs", "error", file_pattern="*.log")
    ```

4. Monitoring (monitor_ops):
    ```python
    from file_toolkit import watch_file

    def on_change(path):
      print(f"{path} changed!")

    stop_flag = watch_file("input.csv", on_change, interval=2.0)
    ```

5. 🔄 Sync (sync_ops):
    ```python
    from file_toolkit import sync_directories

    sync_directories("source/", "target/", delete=True)
    ```

6. Hashing (hash_ops):
    ```python
    from file_toolkit import get_file_hash, find_duplicates

    print(get_file_hash("file.csv"))
    duplicates = find_duplicates("my-folder/")
    ```

7. Stats (stats_ops):
    ```python
    from file_toolkit import check_disk_space, get_largest_files

    total, used, free = check_disk_space()
    largest = get_largest_files("/mnt/data")
    ```

8. Temporary Files (temp_file_utils):
    ```python
    from file_toolkit import create_temp_file

    tmp = create_temp_file(content="temp", suffix=".txt")
    ```

---

## 🏆 Best Practices

- Use logger for all file operations for better auditability.
- Use ProgressPercentage when copying/moving large files.
- Use backup_file() before overwriting critical files.
- Always wrap your I/O logic with error-handling utilities provided.
- Use ignore_patterns in sync_directories() to prevent syncing sensitive files.
 
---


## 🧪 Tests

The library has a complete test suite to ensure quality and reliability.

#### Running the tests:
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
make test

# Tests with coverage
make test-cov

# Specific tests
pytest test/test_file_toolkit.py -v

# Tests with different verbosity levels
pytest test/ -v                     # Verbose
pytest test/ -s                     # No output capture
pytest test/ --tb=short             # Short traceback
```

#### Test Structure
```
test/
├── test_file_ops
  ├── conftest.py                  # Shared pytest fixtures and test configurations        
  ├── Makefile                     # Automation commands for testing, linting, and build tasks
  ├── pytest.ini                   # Global pytest configuration settings
  ├── run_tests.py                 # Script to run all tests automatically
  ├── test-requirements.txt        # Development and test dependencies
  ├── TEST_GUIDE.md                # Quick guide: how to run and interpret tests
  └── test_file_ops.py             # Automated tests for the file_ops library
├── test_hash_ops
  └── ...
├── test_monitor_ops
  └── ...
├── test_progress
  └── ...
├── test_search_ops
  └── ...
├── test_stats_ops
  └── ...
├── test_sync_ops
  └── ...
├── test_temp_file_ops
  └── ...
└── test_zip_ops
  └── ...

```

#### Current coverage
```
# Coverage report
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/logging_metrics/__init__.py     12      0   100%
src/logging_metrics/console.py      45      2    96%
src/logging_metrics/file.py         78      3    96%
src/logging_metrics/spark.py        32      1    97%
src/logging_metrics/timer.py        56      2    96%
src/logging_metrics/metrics.py      89      4    96%
-----------------------------------------------
TOTAL                            312     12    96%
```

#### Running tests in different environments
```bash
# Test in multiple Python versions with tox
pip install tox

tox

# Specific configurations
tox -e py38                # Python 3.8
tox -e py39                # Python 3.9  
tox -e py310               # Python 3.10
tox -e py311               # Python 3.11
tox -e py312               # Python 3.12
tox -e lint                # Only linting
tox -e coverage            # Only coverage
```

#### Running tests in CI/CD
Tests are run automatically in:

---


## 🔧 Requirements

Python: >= 3.8
Dependencies:
- logging-metrics
- pyspark

---

## 📝 Changelog

v0.1.0 – Initial release
- Initial stable version
- File management core modules
- Sync, search, hashing, compression
- Logging and progress tracking
- Modular and testable design

---

## 🤝 Contributing

#### Contributions are welcome!
1. Fork the project
2. Create your feature branch (`git checkout -b feature/file-toolkit`)
3. Commit your changes (`git commit -m 'Add file-toolkit'`)
4. Push to the branch (`git push origin feature/file-toolkit`)
5. Open a Pull Request

---

## License

MIT License. See LICENSE for details.
